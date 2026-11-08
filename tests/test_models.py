import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.models import Order, OrderStatus, Ticket, User


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
        items="Pelota de goma x2",
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
        Order(user_id=999, items="Cuerda", total_cents=500, shipping_address="X")
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
