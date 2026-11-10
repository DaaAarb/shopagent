from collections.abc import Callable, Iterator

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db.session import enable_sqlite_foreign_keys
from app.models import (
    DogSize,
    Order,
    OrderItem,
    OrderStatus,
    Product,
    ProductCategory,
    User,
)
from app.services import OrderService


@pytest.fixture
def session() -> Iterator[Session]:
    """Base de datos SQLite en memoria, nueva y vacía para cada test.

    StaticPool reutiliza una única conexión: con SQLite en memoria, cada
    conexión nueva sería una base de datos distinta (y vacía).
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    enable_sqlite_foreign_keys(engine)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


def _add_user(session: Session, name: str, email: str) -> User:
    user = User(name=name, email=email)
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
    """Fábrica de productos. Cada llamada crea uno con slug distinto."""
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
    """Fixture "fábrica": devuelve una función para crear pedidos a medida.

    Uso: `make_order(alice, status=OrderStatus.SHIPPED)` crea un pedido con
    2 unidades de `ball`; `lines=[(producto, cantidad), ...]` para elegir otras.
    Inserta directamente en la BD (no pasa por el checkout): sirve para
    preparar escenarios, no para probar la creación de pedidos.
    """

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
def order_service(session: Session) -> OrderService:
    return OrderService(session)
