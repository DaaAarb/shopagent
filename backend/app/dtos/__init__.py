"""DTOs (Data Transfer Objects): los mensajes estructurados que cruzan las fronteras.

Son el contrato del backend con el exterior: el frontend los recibe como JSON y
el agente los usará como resultado de sus herramientas. Separados de los modelos
de tabla a propósito:
- Entrada (`…Create`, `…Update`): validan. Los modelos table=True no lo hacen.
- Salida (`…Read`): deciden qué se expone; un campo interno nuevo no se filtra.

Los servicios reciben y devuelven DTOs: las entidades del ORM nunca salen de services/.
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
