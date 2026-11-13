"""Máquina de estados de los pedidos: solo se pasa por las transiciones permitidas."""

import pytest

from app.models import OrderStatus
from app.services import InvalidOrderState, OrderNotFound


def test_pending_order_can_be_paid(order_service, alice, make_order):
    order = make_order(alice, status=OrderStatus.PENDING)

    paid = order_service.pay_order(alice.id, order.id)

    assert paid.status == OrderStatus.PAID


def test_order_follows_the_full_happy_path(order_service, alice, make_order):
    order = make_order(alice, status=OrderStatus.PENDING)

    order_service.pay_order(alice.id, order.id)
    order_service.ship_order(alice.id, order.id)
    delivered = order_service.deliver_order(alice.id, order.id)

    assert delivered.status == OrderStatus.DELIVERED


@pytest.mark.parametrize(
    ("status", "action"),
    [
        (OrderStatus.PENDING, "ship_order"),  # no se envía sin pagar
        (OrderStatus.PENDING, "deliver_order"),  # no se entrega sin pagar ni enviar
        (OrderStatus.PAID, "deliver_order"),  # no se entrega sin enviar
        (OrderStatus.SHIPPED, "pay_order"),  # no se vuelve atrás
        (OrderStatus.SHIPPED, "cancel_order"),  # ya salió: no se cancela
        (OrderStatus.DELIVERED, "cancel_order"),  # estado final
        (OrderStatus.DELIVERED, "ship_order"),  # estado final
        (OrderStatus.CANCELLED, "pay_order"),  # cancelado no vuelve a la vida
        (OrderStatus.CANCELLED, "cancel_order"),  # ni se cancela dos veces
    ],
)
def test_forbidden_transitions_are_rejected(
    order_service, alice, make_order, status, action
):
    order = make_order(alice, status=status)

    with pytest.raises(InvalidOrderState) as error:
        getattr(order_service, action)(alice.id, order.id)

    assert error.value.status == status


@pytest.mark.parametrize("status", [OrderStatus.PENDING, OrderStatus.PAID])
def test_cancel_is_allowed_before_shipping(order_service, alice, make_order, status):
    order = make_order(alice, status=status)

    cancelled = order_service.cancel_order(alice.id, order.id)

    assert cancelled.status == OrderStatus.CANCELLED


def test_rejected_transition_does_not_change_the_order(
    order_service, alice, make_order, session
):
    order = make_order(alice, status=OrderStatus.PENDING)

    with pytest.raises(InvalidOrderState):
        order_service.deliver_order(alice.id, order.id)

    session.refresh(order)
    assert order.status == OrderStatus.PENDING


# --- Cancelar repone el stock ----------------------------------------------------
# Nota: make_order inserta el pedido sin pasar por el checkout, así que no descuenta
# stock; aquí solo se comprueba que cancelar suma lo que el pedido tenía.


def test_cancel_restores_stock_of_every_line(
    order_service, alice, make_order, make_product, session
):
    ball = make_product(stock=5)
    rope = make_product(stock=1)
    order = make_order(alice, lines=[(ball, 2), (rope, 3)])

    order_service.cancel_order(alice.id, order.id)

    session.refresh(ball)
    session.refresh(rope)
    assert ball.stock == 7
    assert rope.stock == 4


def test_rejected_cancel_does_not_touch_stock(
    order_service, alice, make_order, make_product, session
):
    ball = make_product(stock=5)
    order = make_order(alice, status=OrderStatus.SHIPPED, lines=[(ball, 2)])

    with pytest.raises(InvalidOrderState):
        order_service.cancel_order(alice.id, order.id)

    session.refresh(ball)
    assert ball.stock == 5


def test_another_user_cannot_advance_my_order(order_service, alice, bob, make_order):
    order = make_order(alice, status=OrderStatus.PENDING)

    with pytest.raises(OrderNotFound):
        order_service.pay_order(bob.id, order.id)
