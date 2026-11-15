"""Repositorio genérico y unidad de trabajo."""

import pytest

from app.models import Product, User
from app.repositories import Repository


# --- Repository[T]: el mismo código sirve para cualquier modelo -----------------


@pytest.mark.parametrize("repository_name", ["users", "products"])
def test_generic_get_works_for_any_model(uow, alice, ball, repository_name):
    repository: Repository = getattr(uow, repository_name)
    expected = {"users": alice, "products": ball}[repository_name]

    found = repository.get(expected.id)

    assert isinstance(found, repository.model)
    assert found.id == expected.id


def test_get_missing_returns_none(uow):
    assert uow.users.get(999) is None


def test_find_filters_and_orders(uow, make_product):
    cheap = make_product(price_cents=300)
    expensive = make_product(price_cents=900)
    make_product(price_cents=100, stock=0)  # sin stock: no debe salir

    found = uow.products.find(Product.stock > 0, order_by=(Product.price_cents.desc(),))

    assert [p.id for p in found] == [expensive.id, cheap.id]


def test_list_for_user_returns_only_own_orders_newest_first(uow, alice, bob, make_order):
    first = make_order(alice)
    second = make_order(alice)
    make_order(bob)

    assert [o.id for o in uow.orders.list_for_user(alice.id)] == [second.id, first.id]


# --- UnitOfWork: el repositorio no confirma; la unidad de trabajo sí -------------


def test_add_assigns_id_but_rollback_discards_it(uow):
    user = uow.users.add(User(name="Carol", email="carol@example.com"))
    assert user.id is not None  # flush: la BD ya le ha dado id…

    uow.rollback()

    assert uow.users.get(user.id) is None  # …pero sin commit, no se guardó


def test_commit_persists_changes(uow):
    user = uow.users.add(User(name="Carol", email="carol@example.com"))
    uow.commit()

    assert uow.users.get(user.id).email == "carol@example.com"


def test_exception_inside_with_block_rolls_back(uow):
    with pytest.raises(RuntimeError), uow:
        user = uow.users.add(User(name="Carol", email="carol@example.com"))
        raise RuntimeError("algo falla a mitad de la operación")

    assert uow.users.get(user.id) is None
