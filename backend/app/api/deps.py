"""Dependencias de FastAPI: sesión, usuario actual, servicios y agente."""

from functools import lru_cache
from typing import Annotated

from fastapi import Cookie, Depends
from redis import Redis
from sqlmodel import Session

from app.agent.agent import Agent
from app.agent.gemini import GeminiClient
from app.agent.history import ChatStore, RedisChatStore
from app.agent.llm import LLMClient, LLMError
from app.agent.tools import ToolBox, ToolServices
from app.api.errors import NotAuthenticated
from app.config import get_settings
from app.db.session import get_session
from app.repositories import UnitOfWork
from app.security import InvalidToken, read_session_token
from app.services import AuthService, OrderService, ProductService, TicketService, UserService

SessionDep = Annotated[Session, Depends(get_session)]


def get_uow(session: SessionDep) -> UnitOfWork:
    # FastAPI cachea la dependencia por petición: todos los servicios comparten esta UoW.
    return UnitOfWork(session)


UnitOfWorkDep = Annotated[UnitOfWork, Depends(get_uow)]


SESSION_COOKIE = "session"


def get_current_user_id(
    uow: UnitOfWorkDep,
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
) -> int:
    """`user_id` de la cookie de sesión. El resto del backend no conoce el mecanismo de sesión."""
    if session is None:
        raise NotAuthenticated()
    try:
        user_id = read_session_token(session)
    except InvalidToken:
        raise NotAuthenticated() from None
    UserService(uow).get_user(user_id)  # pudo borrarse después de emitir el token
    return user_id


CurrentUserId = Annotated[int, Depends(get_current_user_id)]


def get_auth_service(uow: UnitOfWorkDep) -> AuthService:
    return AuthService(uow)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


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


# --- Agente ---------------------------------------------------------------------------
# Cliente de Gemini y conexión a Redis compartidos entre peticiones. Los tests los
# sustituyen con app.dependency_overrides.


@lru_cache
def _gemini_client(api_key: str, model: str) -> GeminiClient:
    return GeminiClient(api_key=api_key, model=model)


def get_llm() -> LLMClient:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise LLMError("Falta GEMINI_API_KEY en el .env.")
    return _gemini_client(settings.gemini_api_key, settings.llm_model)


@lru_cache
def _redis() -> Redis:
    return Redis.from_url(get_settings().redis_url, socket_connect_timeout=2)


def get_chat_store() -> ChatStore:
    return RedisChatStore(_redis(), ttl_seconds=get_settings().chat_ttl_seconds)


def get_agent(
    llm: Annotated[LLMClient, Depends(get_llm)],
    store: Annotated[ChatStore, Depends(get_chat_store)],
    orders: OrderServiceDep,
    tickets: TicketServiceDep,
) -> Agent:
    return Agent(llm, ToolBox(ToolServices(orders=orders, tickets=tickets)), store)


AgentDep = Annotated[Agent, Depends(get_agent)]
