from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.dtos.common import NonBlank
from app.models import Order, OrderStatus

# --- Entrada --------------------------------------------------------------------


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
        """Construcción a mano (no `from_attributes`) porque `product_name` no es un
        atributo de la línea: hay que leerlo de su producto. Se llama dentro del
        servicio, con la sesión abierta, para que las líneas se puedan cargar."""
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
