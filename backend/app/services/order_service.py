from app.dtos import OrderCreate, OrderRead
from app.models import Order, OrderItem, OrderStatus
from app.repositories import UnitOfWork
from app.services.exceptions import (
    InsufficientStock,
    InvalidInput,
    InvalidOrderState,
    OrderNotFound,
    ProductNotFound,
)


class OrderService:
    """Reglas de negocio y permisos sobre pedidos, compartidos por la API y el agente.

    Cada método recibe el `user_id` de quien pregunta y comprueba la propiedad del pedido.
    """

    # Máquina de estados: cualquier transición no listada se rechaza (409).
    TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]] = {
        OrderStatus.PENDING: frozenset({OrderStatus.PAID, OrderStatus.CANCELLED}),
        OrderStatus.PAID: frozenset({OrderStatus.SHIPPED, OrderStatus.CANCELLED}),
        OrderStatus.SHIPPED: frozenset({OrderStatus.DELIVERED}),
        OrderStatus.DELIVERED: frozenset(),
        OrderStatus.CANCELLED: frozenset(),
    }
    ADDRESS_CHANGEABLE_STATES = frozenset({OrderStatus.PENDING, OrderStatus.PAID})

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def get_order(self, user_id: int, order_id: int) -> OrderRead:
        return OrderRead.from_entity(self._get_owned(user_id, order_id))

    def list_orders(self, user_id: int) -> list[OrderRead]:
        return [OrderRead.from_entity(o) for o in self.uow.orders.list_for_user(user_id)]

    def create_order(self, user_id: int, data: OrderCreate) -> OrderRead:
        """Checkout simulado (sin pago): crea el pedido en `pending` y descuenta stock."""
        # Agrupa líneas repetidas: el stock se comprueba contra el total por producto.
        quantities: dict[int, int] = {}
        for line in data.items:
            quantities[line.product_id] = quantities.get(line.product_id, 0) + line.quantity

        with self.uow:
            # Bloqueo de filas: dos compras simultáneas no venden la misma última unidad.
            products = {p.id: p for p in self.uow.products.lock_by_ids(list(quantities))}

            # Se valida todo antes de modificar nada: el rechazo es del pedido entero.
            for product_id, quantity in quantities.items():
                product = products.get(product_id)
                if product is None:
                    raise ProductNotFound(product_id)
                if product.stock < quantity:
                    raise InsufficientStock(product.name, quantity, product.stock)

            order = Order(
                user_id=user_id,
                total_cents=sum(products[pid].price_cents * qty for pid, qty in quantities.items()),
                shipping_address=data.shipping_address,
                items=[
                    OrderItem(
                        product_id=pid,
                        quantity=qty,
                        unit_price_cents=products[pid].price_cents,
                    )
                    for pid, qty in quantities.items()
                ],
            )
            for pid, qty in quantities.items():
                products[pid].stock -= qty

            self.uow.orders.add(order)
            self.uow.commit()
            return OrderRead.from_entity(order)

    def cancel_order(self, user_id: int, order_id: int) -> OrderRead:
        with self.uow:
            order = self._get_owned(user_id, order_id)
            self._check_transition(order, OrderStatus.CANCELLED, "cancelar")

            # Reposición de stock y cancelación en la misma transacción.
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

    # Avance de estados para los endpoints de demo (simulan pago y logística).
    def pay_order(self, user_id: int, order_id: int) -> OrderRead:
        return self._transition(user_id, order_id, OrderStatus.PAID, "pagar")

    def ship_order(self, user_id: int, order_id: int) -> OrderRead:
        return self._transition(user_id, order_id, OrderStatus.SHIPPED, "enviar")

    def deliver_order(self, user_id: int, order_id: int) -> OrderRead:
        return self._transition(user_id, order_id, OrderStatus.DELIVERED, "entregar")

    # --- Auxiliares --------------------------------------------------------------

    def _get_owned(self, user_id: int, order_id: int) -> Order:
        order = self.uow.orders.get(order_id)
        # Inexistente y ajeno dan el mismo error: no se revela que el pedido existe.
        if order is None or order.user_id != user_id:
            raise OrderNotFound(order_id)
        return order

    def _transition(
        self, user_id: int, order_id: int, new_status: OrderStatus, action: str
    ) -> OrderRead:
        with self.uow:
            order = self._get_owned(user_id, order_id)
            self._check_transition(order, new_status, action)

            order.status = new_status
            self.uow.commit()
            return OrderRead.from_entity(order)

    def _check_transition(self, order: Order, new_status: OrderStatus, action: str) -> None:
        if new_status not in self.TRANSITIONS[order.status]:
            raise InvalidOrderState(order.id, order.status, action)
