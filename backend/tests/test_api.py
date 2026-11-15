"""Tests de la API: HTTP de extremo a extremo contra la BD de tests (PostgreSQL).

La fixture `client` (en conftest.py) inyecta la sesión aislada de cada test.
"""

import pytest

from app.models import OrderStatus
from tests.helpers import as_user


# --- Autenticación simulada ----------------------------------------------------


def test_missing_user_header_returns_401(client):
    response = client.get("/orders")
    assert response.status_code == 401
    assert response.json() == {"detail": "Falta la cabecera X-User-Id."}


def test_unknown_user_returns_401(client):
    assert client.get("/orders", headers={"X-User-Id": "999"}).status_code == 401


def test_users_list_is_public_for_the_demo_selector(client, alice, bob):
    response = client.get("/users")

    assert response.status_code == 200
    assert [u["name"] for u in response.json()] == ["Alice", "Bob"]


# --- Pedidos ---------------------------------------------------------------------


def test_list_orders_returns_own_orders_with_lines(client, alice, bob, make_order, ball):
    order = make_order(alice, lines=[(ball, 3)])
    make_order(bob)

    response = client.get("/orders", headers=as_user(alice))

    assert response.status_code == 200
    [body] = response.json()
    assert body["id"] == order.id
    assert body["total_cents"] == 3 * ball.price_cents
    assert body["items"] == [
        {
            "product_id": ball.id,
            "product_name": ball.name,
            "quantity": 3,
            "unit_price_cents": ball.price_cents,
        }
    ]


def test_get_foreign_order_returns_404(client, alice, bob, make_order):
    bobs_order = make_order(bob)

    response = client.get(f"/orders/{bobs_order.id}", headers=as_user(alice))

    assert response.status_code == 404
    assert response.json() == {"detail": f"Pedido {bobs_order.id} no encontrado."}


def test_cancel_pending_order(client, alice, make_order):
    order = make_order(alice)

    response = client.post(f"/orders/{order.id}/cancel", headers=as_user(alice))

    assert response.status_code == 200
    assert response.json()["status"] == OrderStatus.CANCELLED


def test_cancel_shipped_order_returns_409(client, alice, make_order):
    order = make_order(alice, status=OrderStatus.SHIPPED)

    response = client.post(f"/orders/{order.id}/cancel", headers=as_user(alice))

    assert response.status_code == 409


def test_change_address(client, alice, make_order):
    order = make_order(alice)

    response = client.patch(
        f"/orders/{order.id}/address",
        headers=as_user(alice),
        json={"shipping_address": "  Av. del Puerto 5, Valencia "},
    )

    assert response.status_code == 200
    assert response.json()["shipping_address"] == "Av. del Puerto 5, Valencia"


@pytest.mark.parametrize("payload", [{"shipping_address": "   "}, {}, {"shipping_address": "x" * 201}])
def test_change_address_with_invalid_body_returns_422(client, alice, make_order, payload):
    order = make_order(alice)

    response = client.patch(f"/orders/{order.id}/address", headers=as_user(alice), json=payload)

    assert response.status_code == 422


# --- Tickets ---------------------------------------------------------------------


def test_open_and_list_tickets(client, alice, make_order):
    order = make_order(alice)

    created = client.post(
        "/tickets",
        headers=as_user(alice),
        json={"subject": "Retraso", "description": "No ha llegado", "order_id": order.id},
    )
    listed = client.get("/tickets", headers=as_user(alice))

    assert created.status_code == 201
    assert created.json()["order_id"] == order.id
    assert [t["id"] for t in listed.json()] == [created.json()["id"]]


def test_ticket_about_foreign_order_returns_404(client, alice, bob, make_order):
    bobs_order = make_order(bob)

    response = client.post(
        "/tickets",
        headers=as_user(alice),
        json={"subject": "Hola", "description": "Es mío", "order_id": bobs_order.id},
    )

    assert response.status_code == 404
