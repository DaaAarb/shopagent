from collections.abc import Callable, Iterator

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db.session import enable_sqlite_foreign_keys
from app.models import Order, OrderStatus, User
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
def make_order(session: Session) -> Callable[..., Order]:
    """Fixture "fábrica": devuelve una función para crear pedidos a medida.

    Uso en un test: `order = make_order(alice, status=OrderStatus.SHIPPED)`.
    """

    def _make(
        user: User,
        status: OrderStatus = OrderStatus.PENDING,
        items: str = "Pelota de goma x2",
        total_cents: int = 1298,
        shipping_address: str = "Calle Mayor 1, Valencia",
    ) -> Order:
        order = Order(
            user_id=user.id,
            status=status,
            items=items,
            total_cents=total_cents,
            shipping_address=shipping_address,
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        return order

    return _make


@pytest.fixture
def order_service(session: Session) -> OrderService:
    return OrderService(session)
