from enum import StrEnum


class OrderStatus(StrEnum):
    """Ciclo de vida de un pedido.

    pending → paid → shipped → delivered
       └──────┴──→ cancelled   (solo desde pending o paid)
    """

    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
