from sqlmodel import col

from app.models import Order
from app.repositories.base import Repository


class OrderRepository(Repository[Order]):
    model = Order

    def list_for_user(self, user_id: int) -> list[Order]:
        """Pedidos de un usuario, del más reciente al más antiguo."""
        return self.find(
            Order.user_id == user_id,
            order_by=(col(Order.created_at).desc(), col(Order.id).desc()),
        )
