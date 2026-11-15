"""Endpoints de demo: avanzan el pedido respetando la máquina de estados y la propiedad."""

import pytest

from app.models import OrderStatus
from tests.helpers import as_user


def test_demo_endpoints_walk_the_full_lifecycle(client, alice, make_order):
    order = make_order(alice, status=OrderStatus.PENDING)
    headers = as_user(alice)

    for action, expected in [
        ("pay", "paid"),
        ("ship", "shipped"),
        ("deliver", "delivered"),
    ]:
        response = client.post(f"/demo/orders/{order.id}/{action}", headers=headers)
        assert response.status_code == 200
        assert response.json()["status"] == expected


@pytest.mark.parametrize(
    ("status", "action"),
    [
        (OrderStatus.PENDING, "ship"),  # no se envía sin pagar
        (OrderStatus.PAID, "deliver"),  # no se entrega sin enviar
        (OrderStatus.CANCELLED, "pay"),  # un cancelado no revive
        (OrderStatus.DELIVERED, "pay"),  # no se vuelve atrás
    ],
)
def test_demo_endpoints_reject_invalid_transitions(client, alice, make_order, status, action):
    order = make_order(alice, status=status)

    response = client.post(f"/demo/orders/{order.id}/{action}", headers=as_user(alice))

    assert response.status_code == 409


def test_demo_endpoints_cannot_touch_other_users_orders(client, alice, bob, make_order):
    order = make_order(bob)

    response = client.post(f"/demo/orders/{order.id}/pay", headers=as_user(alice))

    # 404 y no 403: no se revela que el pedido existe.
    assert response.status_code == 404


def test_demo_endpoints_require_user_header(client, alice, make_order):
    order = make_order(alice)

    assert client.post(f"/demo/orders/{order.id}/pay").status_code == 401
