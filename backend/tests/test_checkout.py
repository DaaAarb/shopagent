"""Checkout: crear un pedido descuenta stock, copia precios y es todo o nada."""

import pytest
from pydantic import ValidationError

from app.dtos import OrderCreate, OrderLineCreate
from app.models import OrderStatus
from app.services import InsufficientStock, ProductNotFound
from tests.test_api import as_user, client  # noqa: F401  (fixture `client`)

ADDRESS = "Calle Mayor 1, Valencia"


def checkout(*lines: tuple[int, int], address: str = ADDRESS) -> OrderCreate:
    return OrderCreate(
        items=[OrderLineCreate(product_id=pid, quantity=qty) for pid, qty in lines],
        shipping_address=address,
    )


# --- Servicio --------------------------------------------------------------------


def test_create_order_is_pending_with_lines_and_total(order_service, alice, make_product):
    ball = make_product(price_cents=649)
    bone = make_product(price_cents=999)

    order = order_service.create_order(alice.id, checkout((ball.id, 2), (bone.id, 1)))

    assert order.status == OrderStatus.PENDING
    assert order.total_cents == 2 * 649 + 999
    assert order.shipping_address == ADDRESS
    assert {(i.product_id, i.quantity, i.unit_price_cents) for i in order.items} == {
        (ball.id, 2, 649),
        (bone.id, 1, 999),
    }


def test_create_order_decrements_stock(order_service, alice, make_product, session):
    ball = make_product(stock=10)

    order_service.create_order(alice.id, checkout((ball.id, 3)))

    session.refresh(ball)
    assert ball.stock == 7


def test_order_keeps_the_price_paid_if_the_catalog_changes(
    order_service, alice, make_product, session
):
    ball = make_product(price_cents=649)
    order = order_service.create_order(alice.id, checkout((ball.id, 1)))

    ball.price_cents = 1500
    session.commit()

    assert order_service.get_order(alice.id, order.id).items[0].unit_price_cents == 649


def test_repeated_product_lines_are_merged(order_service, alice, make_product):
    ball = make_product()

    order = order_service.create_order(alice.id, checkout((ball.id, 1), (ball.id, 2)))

    [item] = order.items
    assert item.quantity == 3


def test_repeated_lines_are_checked_against_stock_together(order_service, alice, make_product):
    ball = make_product(stock=2)

    with pytest.raises(InsufficientStock):
        order_service.create_order(alice.id, checkout((ball.id, 1), (ball.id, 2)))


def test_insufficient_stock_rejects_the_whole_order(
    order_service, alice, make_product, session
):
    plenty = make_product(stock=10)
    scarce = make_product(stock=1, name="Hueso escaso")

    with pytest.raises(InsufficientStock, match="Hueso escaso"):
        order_service.create_order(alice.id, checkout((plenty.id, 2), (scarce.id, 5)))

    # Ni se descontó el producto que sí tenía stock, ni se creó el pedido.
    session.refresh(plenty)
    assert plenty.stock == 10
    assert order_service.list_orders(alice.id) == []


def test_can_buy_exactly_the_remaining_stock(order_service, alice, make_product, session):
    ball = make_product(stock=2)

    order_service.create_order(alice.id, checkout((ball.id, 2)))

    session.refresh(ball)
    assert ball.stock == 0


def test_unknown_product_is_rejected(order_service, alice):
    with pytest.raises(ProductNotFound):
        order_service.create_order(alice.id, checkout((9999, 1)))


def test_cancelling_a_new_order_restores_the_stock(
    order_service, alice, make_product, session
):
    ball = make_product(stock=10)
    order = order_service.create_order(alice.id, checkout((ball.id, 4)))

    order_service.cancel_order(alice.id, order.id)

    session.refresh(ball)
    assert ball.stock == 10


# --- Validación de entrada (DTO) ---------------------------------------------------


@pytest.mark.parametrize("quantity", [0, -1, 100])
def test_quantity_must_be_between_1_and_99(quantity):
    with pytest.raises(ValidationError):
        OrderLineCreate(product_id=1, quantity=quantity)


def test_order_needs_at_least_one_line():
    with pytest.raises(ValidationError):
        OrderCreate(items=[], shipping_address=ADDRESS)


def test_shipping_address_cannot_be_blank():
    with pytest.raises(ValidationError):
        checkout((1, 1), address="   ")


# --- API -------------------------------------------------------------------------


def test_post_orders_creates_the_order(client, alice, make_product):  # noqa: F811
    ball = make_product(price_cents=649, stock=5)

    response = client.post(
        "/orders",
        headers=as_user(alice),
        json={"items": [{"product_id": ball.id, "quantity": 2}], "shipping_address": ADDRESS},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["total_cents"] == 2 * 649


def test_post_orders_without_stock_returns_409(client, alice, make_product):  # noqa: F811
    ball = make_product(stock=1)

    response = client.post(
        "/orders",
        headers=as_user(alice),
        json={"items": [{"product_id": ball.id, "quantity": 2}], "shipping_address": ADDRESS},
    )

    assert response.status_code == 409
    assert "Stock insuficiente" in response.json()["detail"]


def test_post_orders_with_unknown_product_returns_404(client, alice):  # noqa: F811
    response = client.post(
        "/orders",
        headers=as_user(alice),
        json={"items": [{"product_id": 9999, "quantity": 1}], "shipping_address": ADDRESS},
    )

    assert response.status_code == 404


def test_post_orders_with_empty_cart_returns_422(client, alice):  # noqa: F811
    response = client.post(
        "/orders",
        headers=as_user(alice),
        json={"items": [], "shipping_address": ADDRESS},
    )

    assert response.status_code == 422


def test_post_orders_requires_user_header(client):  # noqa: F811
    response = client.post(
        "/orders", json={"items": [{"product_id": 1, "quantity": 1}], "shipping_address": ADDRESS}
    )

    assert response.status_code == 401
