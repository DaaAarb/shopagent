import pytest

from app.services import (
    InvalidInput,
    OrderNotFound,
    TicketService,
    UserNotFound,
    UserService,
)


@pytest.fixture
def ticket_service(session) -> TicketService:
    return TicketService(session)


@pytest.fixture
def user_service(session) -> UserService:
    return UserService(session)


# --- TicketService --------------------------------------------------------------


def test_open_ticket_without_order(ticket_service, alice):
    ticket = ticket_service.open_ticket(alice.id, "Envíos", "¿Enviáis a Canarias?")

    assert ticket.id is not None
    assert ticket.order_id is None


def test_open_ticket_about_own_order(ticket_service, alice, make_order):
    order = make_order(alice)

    ticket = ticket_service.open_ticket(alice.id, "Retraso", "No llega", order_id=order.id)

    assert ticket.order_id == order.id


def test_cannot_open_ticket_about_another_users_order(ticket_service, alice, bob, make_order):
    bobs_order = make_order(bob)

    with pytest.raises(OrderNotFound):
        ticket_service.open_ticket(alice.id, "Hola", "Es mío", order_id=bobs_order.id)

    assert ticket_service.list_tickets(alice.id) == []


@pytest.mark.parametrize(("subject", "description"), [("", "algo"), ("Asunto", "   ")])
def test_ticket_requires_subject_and_description(ticket_service, alice, subject, description):
    with pytest.raises(InvalidInput):
        ticket_service.open_ticket(alice.id, subject, description)


def test_list_tickets_returns_only_own(ticket_service, alice, bob):
    ticket_service.open_ticket(bob.id, "De Bob", "...")
    mine = ticket_service.open_ticket(alice.id, "De Alice", "...")

    assert [t.id for t in ticket_service.list_tickets(alice.id)] == [mine.id]


# --- UserService ----------------------------------------------------------------


def test_get_existing_user(user_service, alice):
    assert user_service.get_user(alice.id).email == "alice@example.com"


def test_get_missing_user_raises(user_service):
    with pytest.raises(UserNotFound):
        user_service.get_user(999)


def test_list_users_in_id_order(user_service, alice, bob):
    assert [u.id for u in user_service.list_users()] == [alice.id, bob.id]
