"""Endpoints de DEMO: sustituyen a la pasarela de pago y a la empresa de transporte.

En una tienda real, el pago lo confirmaría la pasarela y el envío/entrega el
transportista. Aquí se avanzan a mano para poder enseñar todo el ciclo de vida.
No son un atajo: pasan por la misma máquina de estados y la misma comprobación
de propiedad que el resto (no se puede enviar un pedido sin pagar, ni tocar uno ajeno).
"""

from fastapi import APIRouter

from app.api.deps import CurrentUserId, OrderServiceDep
from app.dtos import OrderRead

router = APIRouter(prefix="/demo/orders", tags=["demo"])


@router.post("/{order_id}/pay", response_model=OrderRead)
def pay_order(order_id: int, user_id: CurrentUserId, orders: OrderServiceDep):
    return orders.pay_order(user_id, order_id)


@router.post("/{order_id}/ship", response_model=OrderRead)
def ship_order(order_id: int, user_id: CurrentUserId, orders: OrderServiceDep):
    return orders.ship_order(user_id, order_id)


@router.post("/{order_id}/deliver", response_model=OrderRead)
def deliver_order(order_id: int, user_id: CurrentUserId, orders: OrderServiceDep):
    return orders.deliver_order(user_id, order_id)
