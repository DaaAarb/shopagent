from fastapi import APIRouter, status

from app.api.deps import CurrentUserId, OrderServiceDep
from app.dtos import AddressUpdate, OrderCreate, OrderRead

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(body: OrderCreate, user_id: CurrentUserId, orders: OrderServiceDep):
    """Checkout simulado: crea el pedido (pending) y descuenta el stock."""
    return orders.create_order(user_id, body)


@router.get("", response_model=list[OrderRead])
def list_orders(user_id: CurrentUserId, orders: OrderServiceDep):
    return orders.list_orders(user_id)


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, user_id: CurrentUserId, orders: OrderServiceDep):
    return orders.get_order(user_id, order_id)


@router.post("/{order_id}/cancel", response_model=OrderRead)
def cancel_order(order_id: int, user_id: CurrentUserId, orders: OrderServiceDep):
    # Acción explícita en vez de PATCH {"status": ...}: el cliente no puede
    # pedir un estado arbitrario, solo lo que el negocio permite.
    return orders.cancel_order(user_id, order_id)


@router.patch("/{order_id}/address", response_model=OrderRead)
def change_address(
    order_id: int, body: AddressUpdate, user_id: CurrentUserId, orders: OrderServiceDep
):
    return orders.change_address(user_id, order_id, body.shipping_address)
