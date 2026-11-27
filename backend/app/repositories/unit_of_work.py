"""Unidad de trabajo: los repositorios comparten una sesión y se confirman juntos.

    with self.uow:               # rollback automático si hay excepción
        order = self.uow.orders.get(order_id)
        ...
        self.uow.commit()
"""

from types import TracebackType
from typing import Self

from sqlmodel import Session

from app.repositories.orders import OrderRepository
from app.repositories.products import ProductRepository
from app.repositories.tickets import TicketRepository
from app.repositories.users import UserRepository


class UnitOfWork:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.products = ProductRepository(session)
        self.orders = OrderRepository(session)
        self.tickets = TicketRepository(session)

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        # Rollback si el bloque falla; la excepción se propaga.
        if exc_type is not None:
            self.rollback()
