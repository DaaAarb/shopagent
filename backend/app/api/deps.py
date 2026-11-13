"""Dependencias de FastAPI: lo que las rutas reciben "inyectado"."""

from typing import Annotated

from fastapi import Depends, Header
from sqlmodel import Session

from app.api.errors import NotAuthenticated
from app.db.session import get_session
from app.services import OrderService, TicketService, UserService

SessionDep = Annotated[Session, Depends(get_session)]


def get_current_user_id(
    session: SessionDep,
    x_user_id: Annotated[int | None, Header()] = None,
) -> int:
    """Autenticación SIMULADA: quien llama dice quién es con la cabecera X-User-Id.

    En un sistema real aquí se validaría un token. Lo importante es que el
    resto del código recibe un `user_id` ya comprobado y no le importa de dónde sale.
    """
    if x_user_id is None:
        raise NotAuthenticated()  # → 401 (ver api/errors.py)
    UserService(session).get_user(x_user_id)
    return x_user_id


CurrentUserId = Annotated[int, Depends(get_current_user_id)]


def get_order_service(session: SessionDep) -> OrderService:
    return OrderService(session)


def get_ticket_service(session: SessionDep) -> TicketService:
    return TicketService(session)


def get_user_service(session: SessionDep) -> UserService:
    return UserService(session)


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
TicketServiceDep = Annotated[TicketService, Depends(get_ticket_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
