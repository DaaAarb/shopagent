from app.dtos import OrderRead
from app.models import Order, OrderStatus
from app.repositories import UnitOfWork
from app.services.exceptions import InvalidInput, InvalidOrderState, OrderNotFound


class OrderService:
    """Reglas de negocio y permisos sobre pedidos.

    Única puerta de entrada para leer o modificar pedidos: la API y el agente
    llaman a esta clase. Todo método recibe el `user_id` de quien pregunta y
    comprueba que el pedido es suyo. Devuelve DTOs: las entidades no salen de aquí.
    """

    # Máquina de estados: para cada estado, a qué estados puede pasar.
    # Cualquier otro cambio (saltarse un paso, volver atrás) se rechaza con 409.
    TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]] = {
        OrderStatus.PENDING: frozenset({OrderStatus.PAID, OrderStatus.CANCELLED}),
        OrderStatus.PAID: frozenset({OrderStatus.SHIPPED, OrderStatus.CANCELLED}),
        OrderStatus.SHIPPED: frozenset({OrderStatus.DELIVERED}),
        OrderStatus.DELIVERED: frozenset(),
        OrderStatus.CANCELLED: frozenset(),
    }
    ADDRESS_CHANGEABLE_STATES = frozenset({OrderStatus.PENDING, OrderStatus.PAID})

    def __init__(self, uow: UnitOfWork) -> None:
        # La unidad de trabajo se inyecta: da acceso a los repositorios y a la transacción.
        self.uow = uow

    def get_order(self, user_id: int, order_id: int) -> OrderRead:
        return OrderRead.from_entity(self._get_owned(user_id, order_id))

    def list_orders(self, user_id: int) -> list[OrderRead]:
        """Pedidos del usuario, del más reciente al más antiguo."""
        return [OrderRead.from_entity(o) for o in self.uow.orders.list_for_user(user_id)]

    def cancel_order(self, user_id: int, order_id: int) -> OrderRead:
        with self.uow:
            order = self._get_owned(user_id, order_id)
            self._check_transition(order, OrderStatus.CANCELLED, "cancelar")

            # Reponer el stock y cancelar van en UNA transacción (un único commit):
            # o se guardan las dos cosas o ninguna. Nunca queda un pedido cancelado
            # con el stock sin devolver, ni stock devuelto de un pedido vivo.
            for item in order.items:
                item.product.stock += item.quantity
            order.status = OrderStatus.CANCELLED

            self.uow.commit()
            return OrderRead.from_entity(order)

    def change_address(self, user_id: int, order_id: int, new_address: str) -> OrderRead:
        with self.uow:
            order = self._get_owned(user_id, order_id)
            if order.status not in self.ADDRESS_CHANGEABLE_STATES:
                raise InvalidOrderState(order_id, order.status, "cambiar la dirección de")

            address = new_address.strip()
            if not address:
                raise InvalidInput("La dirección de envío no puede estar vacía.")

            order.shipping_address = address
            self.uow.commit()
            return OrderRead.from_entity(order)

    # Avance de estados: los usa el endpoint de demo (sustituyen a la pasarela de pago
    # y a la logística reales). Pasan por la misma máquina de estados que la cancelación.
    def pay_order(self, user_id: int, order_id: int) -> OrderRead:
        return self._transition(user_id, order_id, OrderStatus.PAID, "pagar")

    def ship_order(self, user_id: int, order_id: int) -> OrderRead:
        return self._transition(user_id, order_id, OrderStatus.SHIPPED, "enviar")

    def deliver_order(self, user_id: int, order_id: int) -> OrderRead:
        return self._transition(user_id, order_id, OrderStatus.DELIVERED, "entregar")

    # --- Auxiliares (trabajan con entidades; por eso son privados) ----------------

    def _get_owned(self, user_id: int, order_id: int) -> Order:
        order = self.uow.orders.get(order_id)
        # Inexistente y ajeno se tratan igual: no se revela que el pedido existe.
        if order is None or order.user_id != user_id:
            raise OrderNotFound(order_id)
        return order

    def _transition(
        self, user_id: int, order_id: int, new_status: OrderStatus, action: str
    ) -> OrderRead:
        """Cambio de estado sin efectos extra (pagar, enviar, entregar)."""
        with self.uow:
            order = self._get_owned(user_id, order_id)
            self._check_transition(order, new_status, action)

            order.status = new_status
            self.uow.commit()
            return OrderRead.from_entity(order)

    def _check_transition(self, order: Order, new_status: OrderStatus, action: str) -> None:
        """Único punto que decide si un cambio de estado está permitido."""
        if new_status not in self.TRANSITIONS[order.status]:
            raise InvalidOrderState(order.id, order.status, action)
