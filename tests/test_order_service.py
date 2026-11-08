import pytest

from app.models import OrderStatus
from app.services import InvalidInput, InvalidOrderState, OrderNotFound

# --- get_order: propiedad -----------------------------------------------------


def test_get_order_returns_own_order(order_service, alice, make_order):
    order = make_order(alice)

    assert order_service.get_order(alice.id, order.id).id == order.id


def test_get_order_of_another_user_raises_not_found(order_service, alice, bob, make_order):
    bobs_order = make_order(bob)

    with pytest.raises(OrderNotFound):
        order_service.get_order(alice.id, bobs_order.id)


def test_get_nonexistent_order_raises_not_found(order_service, alice):
    with pytest.raises(OrderNotFound):
        order_service.get_order(alice.id, 999)


def test_foreign_and_missing_orders_give_identical_error(
    order_service, alice, bob, make_order
):
    """Un atacante no debe poder distinguir "existe pero no es tuyo" de "no existe"."""
    bobs_order = make_order(bob)
    missing_id = bobs_order.id + 1

    with pytest.raises(OrderNotFound) as foreign:
        order_service.get_order(alice.id, bobs_order.id)
    with pytest.raises(OrderNotFound) as missing:
        order_service.get_order(alice.id, missing_id)

    assert str(foreign.value) == f"Pedido {bobs_order.id} no encontrado."
    assert str(missing.value) == f"Pedido {missing_id} no encontrado."


# --- list_orders ----------------------------------------------------------------


def test_list_orders_returns_only_own_orders(order_service, alice, bob, make_order):
    first = make_order(alice)
    second = make_order(alice)
    make_order(bob)

    orders = order_service.list_orders(alice.id)

    assert [o.id for o in orders] == [second.id, first.id]  # más reciente primero


def test_list_orders_of_user_without_orders_is_empty(order_service, alice):
    assert order_service.list_orders(alice.id) == []


# --- cancel_order ---------------------------------------------------------------


@pytest.mark.parametrize("status", [OrderStatus.PENDING, OrderStatus.PAID])
def test_cancel_allowed_before_shipping(order_service, alice, make_order, status):
    order = make_order(alice, status=status)

    cancelled = order_service.cancel_order(alice.id, order.id)

    assert cancelled.status == OrderStatus.CANCELLED


@pytest.mark.parametrize(
    "status", [OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED]
)
def test_cancel_rejected_in_other_states(order_service, alice, make_order, status):
    order = make_order(alice, status=status)

    with pytest.raises(InvalidOrderState):
        order_service.cancel_order(alice.id, order.id)

    assert order_service.get_order(alice.id, order.id).status == status  # no cambió


def test_cannot_cancel_another_users_order(order_service, alice, bob, make_order):
    bobs_order = make_order(bob)

    with pytest.raises(OrderNotFound):
        order_service.cancel_order(alice.id, bobs_order.id)

    assert order_service.get_order(bob.id, bobs_order.id).status == OrderStatus.PENDING


# --- change_address -------------------------------------------------------------


@pytest.mark.parametrize("status", [OrderStatus.PENDING, OrderStatus.PAID])
def test_change_address_allowed_before_shipping(order_service, alice, make_order, status):
    order = make_order(alice, status=status)

    updated = order_service.change_address(alice.id, order.id, "  Av. del Puerto 5, Valencia  ")

    assert updated.shipping_address == "Av. del Puerto 5, Valencia"


@pytest.mark.parametrize(
    "status", [OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED]
)
def test_change_address_rejected_from_shipping_on(order_service, alice, make_order, status):
    order = make_order(alice, status=status)

    with pytest.raises(InvalidOrderState):
        order_service.change_address(alice.id, order.id, "Otra calle 2")


@pytest.mark.parametrize("address", ["", "   "])
def test_change_address_rejects_blank_address(order_service, alice, make_order, address):
    order = make_order(alice)

    with pytest.raises(InvalidInput):
        order_service.change_address(alice.id, order.id, address)


def test_cannot_change_address_of_another_users_order(order_service, alice, bob, make_order):
    bobs_order = make_order(bob)

    with pytest.raises(OrderNotFound):
        order_service.change_address(alice.id, bobs_order.id, "Calle del ladrón 1")

    unchanged = order_service.get_order(bob.id, bobs_order.id)
    assert unchanged.shipping_address == "Calle Mayor 1, Valencia"
