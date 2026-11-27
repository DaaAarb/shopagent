"""DTOs: el contrato del backend con el frontend y con las herramientas del agente.

- Entrada (`…Create`, `…Update`, `…Request`): validan los datos recibidos.
- Salida (`…Read`): fijan qué se expone, así un campo interno nuevo no se filtra.
"""

from app.dtos.auth import LoginRequest, RegisterRequest
from app.dtos.chat import ChatConfirm, ChatMessageCreate
from app.dtos.orders import (
    AddressUpdate,
    OrderCreate,
    OrderItemRead,
    OrderLineCreate,
    OrderRead,
)
from app.dtos.products import ProductRead
from app.dtos.tickets import TicketCreate, TicketRead
from app.dtos.users import UserRead

__all__ = [
    "AddressUpdate",
    "ChatConfirm",
    "ChatMessageCreate",
    "LoginRequest",
    "OrderCreate",
    "OrderItemRead",
    "OrderLineCreate",
    "OrderRead",
    "ProductRead",
    "RegisterRequest",
    "TicketCreate",
    "TicketRead",
    "UserRead",
]
