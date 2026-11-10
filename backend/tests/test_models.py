import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.models import Order, OrderItem, OrderStatus, Ticket, User


def make_user(session: Session, email: str = "ana@example.com") -> User:
    user = User(name="Ana", email=email)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_order_status_has_exactly_the_five_business_states():
    assert {s.value for s in OrderStatus} == {
        "pending",
        "paid",
        "shipped",
        "delivered",
        "cancelled",
    }


def test_new_order_defaults_to_pending_and_records_creation_time(session: Session):
    user = make_user(session)
    order = Order(
        user_id=user.id,
        total_cents=1298,
        shipping_address="Calle Mayor 1, Valencia",
    )
    session.add(order)
    session.commit()
    session.refresh(order)

    assert order.id is not None
    assert order.status == OrderStatus.PENDING
    assert order.created_at is not None


def test_order_for_nonexistent_user_is_rejected(session: Session):
    session.add(
        Order(user_id=999, total_cents=500, shipping_address="X")
    )

    with pytest.raises(IntegrityError):
        session.commit()


def test_user_email_must_be_unique(session: Session):
    make_user(session, email="ana@example.com")
    session.add(User(name="Otra Ana", email="ana@example.com"))

    with pytest.raises(IntegrityError):
        session.commit()


def test_ticket_can_be_opened_without_an_order(session: Session):
    user = make_user(session)
    ticket = Ticket(user_id=user.id, subject="Duda", description="¿Hacéis envíos a Canarias?")
    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    assert ticket.id is not None
    assert ticket.order_id is None


def test_order_items_keep_price_paid_even_if_catalog_price_changes(
    session: Session, alice, ball, make_order
):
    order = make_order(alice, lines=[(ball, 3)])

    ball.price_cents = 999  # el catálogo sube el precio después de la compra
    session.add(ball)
    session.commit()
    session.refresh(order)

    [line] = order.items
    assert line.quantity == 3
    assert line.unit_price_cents == 649
    assert order.total_cents == 3 * 649


def test_order_item_for_nonexistent_product_is_rejected(session: Session, alice):
    order = Order(user_id=alice.id, total_cents=0, shipping_address="X")
    order.items = [OrderItem(product_id=999, quantity=1, unit_price_cents=100)]
    session.add(order)

    with pytest.raises(IntegrityError):
        session.commit()


def test_product_slug_must_be_unique(session: Session, make_product):
    make_product(slug="pelota-saltarina")

    with pytest.raises(IntegrityError):
        make_product(slug="pelota-saltarina")
