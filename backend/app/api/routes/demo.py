"""Endpoints de demo que simulan la pasarela de pago y el transportista.

Pasan por la misma máquina de estados y comprobación de propiedad que el resto.
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
