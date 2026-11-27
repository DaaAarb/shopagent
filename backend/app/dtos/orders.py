from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.dtos.common import NonBlank
from app.models import Order, OrderStatus

# --- Entrada --------------------------------------------------------------------


class OrderLineCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=99)


class OrderCreate(BaseModel):
    """Checkout: el carrito completo más la dirección de envío."""

    items: list[OrderLineCreate] = Field(min_length=1)
    shipping_address: Annotated[NonBlank, StringConstraints(max_length=200)]


class AddressUpdate(BaseModel):
    shipping_address: Annotated[NonBlank, StringConstraints(max_length=200)]


# --- Salida ---------------------------------------------------------------------


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
    def from_entity(cls, order: Order) -> "OrderRead":
        """`product_name` sale del producto de cada línea, así que se construye a mano.

        Debe llamarse con la sesión abierta para poder cargar las líneas.
        """
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
