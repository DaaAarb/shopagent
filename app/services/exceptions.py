"""Errores del dominio.

Los servicios no saben nada de HTTP ni del LLM: solo lanzan estas excepciones.
- api/   las traduce a códigos HTTP (404, 409, 422).
- agent/ las traduce a mensajes que el modelo entiende.
"""

from app.models import OrderStatus


class ShopError(Exception):
    """Base de todos los errores del dominio (permite capturarlos de una vez)."""


class OrderNotFound(ShopError):
    """El pedido no existe o no pertenece al usuario.

    Ambos casos dan el mismo error a propósito: así no se revela
    que existe un pedido de otra persona con ese id.
    """

    def __init__(self, order_id: int) -> None:
        self.order_id = order_id
        super().__init__(f"Pedido {order_id} no encontrado.")


class InvalidOrderState(ShopError):
    """El estado actual del pedido no permite la acción pedida."""

    def __init__(self, order_id: int, status: OrderStatus, action: str) -> None:
        self.order_id = order_id
        self.status = status
        self.action = action
        super().__init__(
            f"No se puede {action} el pedido {order_id}: está en estado '{status}'."
        )


class InvalidInput(ShopError):
    """Los datos recibidos no son válidos (p. ej. una dirección vacía)."""
