"""Dependencias de FastAPI: lo que las rutas reciben "inyectado"."""

from typing import Annotated

from fastapi import Depends, Header
from sqlmodel import Session

from app.api.errors import NotAuthenticated
from app.db.session import get_session
from app.repositories import UnitOfWork
from app.services import OrderService, ProductService, TicketService, UserService

SessionDep = Annotated[Session, Depends(get_session)]


def get_uow(session: SessionDep) -> UnitOfWork:
    # FastAPI reutiliza el resultado de una dependencia dentro de la misma petición:
    # todos los servicios de una petición comparten esta unidad de trabajo (y su sesión).
    return UnitOfWork(session)


UnitOfWorkDep = Annotated[UnitOfWork, Depends(get_uow)]


def get_current_user_id(
    uow: UnitOfWorkDep,
    x_user_id: Annotated[int | None, Header()] = None,
) -> int:
    """Autenticación SIMULADA: quien llama dice quién es con la cabecera X-User-Id.

    En un sistema real aquí se validaría un token. Lo importante es que el
    resto del código recibe un `user_id` ya comprobado y no le importa de dónde sale.
    """
    if x_user_id is None:
        raise NotAuthenticated()  # → 401 (ver api/errors.py)
    UserService(uow).get_user(x_user_id)
    return x_user_id


CurrentUserId = Annotated[int, Depends(get_current_user_id)]


def get_order_service(uow: UnitOfWorkDep) -> OrderService:
    return OrderService(uow)


def get_product_service(uow: UnitOfWorkDep) -> ProductService:
    return ProductService(uow)


def get_ticket_service(uow: UnitOfWorkDep) -> TicketService:
    return TicketService(uow)


def get_user_service(uow: UnitOfWorkDep) -> UserService:
    return UserService(uow)


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
TicketServiceDep = Annotated[TicketService, Depends(get_ticket_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
