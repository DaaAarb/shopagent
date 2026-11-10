"""Esquemas de entrada y salida de la API.

Separados de los modelos de tabla a propósito:
- Entrada: validan (los modelos table=True no lo hacen). Datos inválidos → 422 automático.
- Salida: deciden qué campos se exponen; un campo interno nuevo no se filtra por accidente.
"""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.models import Order, OrderStatus

NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

# --- Entrada --------------------------------------------------------------------


class AddressUpdate(BaseModel):
    shipping_address: Annotated[NonBlank, StringConstraints(max_length=200)]


class TicketCreate(BaseModel):
    subject: Annotated[NonBlank, StringConstraints(max_length=120)]
    description: Annotated[NonBlank, StringConstraints(max_length=2000)]
    order_id: int | None = None


# --- Salida ---------------------------------------------------------------------


class UserRead(BaseModel):
    id: int
    name: str
    email: str


class OrderItemRead(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price_cents: int


class OrderRead(BaseModel):
    id: int
    status: OrderStatus
    total_cents: int
    shipping_address: str
    created_at: datetime
    items: list[OrderItemRead]

    @classmethod
    def from_order(cls, order: Order) -> "OrderRead":
        """Construye la respuesta mientras la sesión sigue abierta (carga las líneas)."""
        return cls(
            id=order.id,
            status=order.status,
            total_cents=order.total_cents,
            shipping_address=order.shipping_address,
            created_at=order.created_at,
            items=[
                OrderItemRead(
                    product_id=item.product_id,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    unit_price_cents=item.unit_price_cents,
                )
                for item in order.items
            ],
        )


class TicketRead(BaseModel):
    id: int
    order_id: int | None
    subject: str
    description: str
    created_at: datetime
