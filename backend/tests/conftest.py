from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text
from sqlalchemy.exc import OperationalError
from sqlmodel import Session, create_engine

from app.config import get_settings
from app.db.session import get_session
from app.main import app
from app.models import (
    DogSize,
    Order,
    OrderItem,
    OrderStatus,
    Product,
    ProductCategory,
    User,
)
from app.repositories import UnitOfWork
from app.security import hash_password
from app.services import OrderService

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"

# Se hashea una sola vez: argon2 es lento a propósito.
TEST_PASSWORD = "contraseña-de-prueba"
TEST_PASSWORD_HASH = hash_password(TEST_PASSWORD)


@pytest.fixture(autouse=True)
def secret_key(monkeypatch):
    """Clave de firma fija: los tests no dependen del .env."""
    monkeypatch.setattr(get_settings(), "secret_key", "clave-solo-para-tests")


def alembic_config(connection) -> Config:
    config = Config(str(ALEMBIC_INI))
    config.attributes["connection"] = connection
    return config


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    """BD de tests recreada con las migraciones (mismo esquema que producción)."""
    engine = create_engine(
        get_settings().test_database_url, connect_args={"connect_timeout": 5}
    )
    try:
        with engine.begin() as connection:
            connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
            connection.execute(text("CREATE SCHEMA public"))
            command.upgrade(alembic_config(connection), "head")
    except OperationalError as exc:
        pytest.exit(
            "No se puede conectar al PostgreSQL de tests "
            f"({engine.url.render_as_string(hide_password=True)}).\n"
            "Arráncalo con: docker compose up -d db\n"
            f"Detalle: {exc.orig}",
            returncode=1,
        )

    yield engine
    engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    """Sesión aislada: los `commit()` son SAVEPOINTs y todo se revierte al acabar el test."""
    with engine.connect() as connection:
        transaction = connection.begin()
        with Session(bind=connection, join_transaction_mode="create_savepoint") as session:
            yield session
        if transaction.is_active:
            transaction.rollback()


def _add_user(session: Session, name: str, email: str) -> User:
    user = User(name=name, email=email, password_hash=TEST_PASSWORD_HASH)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def alice(session: Session) -> User:
    return _add_user(session, "Alice", "alice@example.com")


@pytest.fixture
def bob(session: Session) -> User:
    return _add_user(session, "Bob", "bob@example.com")


@pytest.fixture
def make_product(session: Session) -> Callable[..., Product]:
    counter = 0

    def _make(price_cents: int = 649, stock: int = 10, **overrides) -> Product:
        nonlocal counter
        counter += 1
        product = Product(
            slug=overrides.pop("slug", f"juguete-{counter}"),
            name=overrides.pop("name", f"Juguete {counter}"),
            category=overrides.pop("category", ProductCategory.BALLS),
            description="Juguete de prueba.",
            price_cents=price_cents,
            stock=stock,
            material="Caucho natural",
            dog_size=DogSize.ALL,
            **overrides,
        )
        session.add(product)
        session.commit()
        session.refresh(product)
        return product

    return _make


@pytest.fixture
def ball(make_product) -> Product:
    return make_product(slug="pelota", name="Pelota de prueba", price_cents=649)


@pytest.fixture
def make_order(session: Session, ball: Product) -> Callable[..., Order]:
    """Crea pedidos directamente en la BD (sin checkout) para preparar escenarios."""

    def _make(
        user: User,
        status: OrderStatus = OrderStatus.PENDING,
        lines: list[tuple[Product, int]] | None = None,
        shipping_address: str = "Calle Mayor 1, Valencia",
    ) -> Order:
        lines = lines or [(ball, 2)]
        order = Order(
            user_id=user.id,
            status=status,
            total_cents=sum(p.price_cents * qty for p, qty in lines),
            shipping_address=shipping_address,
            items=[
                OrderItem(product_id=p.id, quantity=qty, unit_price_cents=p.price_cents)
                for p, qty in lines
            ],
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        return order

    return _make


@pytest.fixture
def client(session: Session) -> Iterator[TestClient]:
    """Cliente HTTP que usa la sesión aislada del test."""
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def uow(session: Session) -> UnitOfWork:
    return UnitOfWork(session)


@pytest.fixture
def order_service(uow: UnitOfWork) -> OrderService:
    return OrderService(uow)
