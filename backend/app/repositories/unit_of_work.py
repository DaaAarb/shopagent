"""Unidad de trabajo (Unit of Work): una transacción que agrupa varios repositorios.

Una operación de negocio puede tocar varias tablas a la vez (cancelar un pedido
cambia el pedido y repone el stock de sus productos). Todos los repositorios
comparten la misma sesión y solo la UnitOfWork confirma: o se guarda todo, o nada.

Uso desde un servicio:

    with self.uow:               # si algo lanza una excepción → rollback automático
        order = self.uow.orders.get(order_id)
        ...
        self.uow.commit()        # un único commit para todos los cambios
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

    # `with uow:` llama a __enter__ al entrar y a __exit__ al salir (con o sin error).
    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        # Si el bloque falló, se deshace lo que no se llegó a confirmar.
        # La excepción sigue subiendo (no devolvemos True): no se oculta el error.
        if exc_type is not None:
            self.rollback()
