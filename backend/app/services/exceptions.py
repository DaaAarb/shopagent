"""Errores del dominio. api/ los traduce a HTTP (404, 409, 422) y agent/ a mensajes para el modelo."""

from app.models import OrderStatus


class ShopError(Exception):
    """Base de los errores del dominio."""


class OrderNotFound(ShopError):
    """El pedido no existe o no pertenece al usuario (mismo error: no se revela que existe)."""

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


class ProductNotFound(ShopError):
    """El producto pedido no existe en el catálogo."""

    def __init__(self, product_id: int | str) -> None:
        self.product_id = product_id
        super().__init__(f"Producto {product_id} no encontrado.")


class InsufficientStock(ShopError):
    """No hay unidades suficientes de un producto: el pedido se rechaza entero."""

    def __init__(self, product_name: str, requested: int, available: int) -> None:
        self.product_name = product_name
        self.requested = requested
        self.available = available
        super().__init__(
            f"Stock insuficiente de '{product_name}': "
            f"pides {requested} y quedan {available}."
        )


class InvalidCredentials(ShopError):
    """Email o contraseña incorrectos (mismo error: no se revela si el email existe)."""

    def __init__(self) -> None:
        super().__init__("Email o contraseña incorrectos.")


class EmailAlreadyRegistered(ShopError):
    def __init__(self) -> None:
        super().__init__("Ya existe una cuenta con ese email.")


class UserNotFound(ShopError):
    """El usuario del token ya no existe (p. ej. se borró tras iniciar sesión)."""

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        super().__init__(f"Usuario {user_id} no encontrado.")


class InvalidInput(ShopError):
    """Los datos recibidos no son válidos (p. ej. una dirección vacía)."""
