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


class ProductCategory(StrEnum):
    BALLS = "balls"
    CHEW = "chew"
    ROPE = "rope"
    PLUSH = "plush"
    INTERACTIVE = "interactive"


class DogSize(StrEnum):
    """Tamaño de perro recomendado. Es información, no una variante del producto."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ALL = "all"
