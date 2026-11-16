"""Herramientas del agente: validación, ejecución con permisos y marca de destructivas."""

import pytest

from app.agent.llm import ToolCall
from app.agent.tools import InvalidToolCall, ToolBox, ToolServices
from app.models import OrderStatus
from app.services import TicketService


@pytest.fixture
def toolbox(order_service, uow) -> ToolBox:
    return ToolBox(ToolServices(orders=order_service, tickets=TicketService(uow)))


def call(name: str, **arguments) -> ToolCall:
    return ToolCall(name=name, arguments=arguments)


# --- Lo que ve el modelo ---------------------------------------------------------------


def test_specs_describe_the_five_tools(toolbox):
    names = {spec.name for spec in toolbox.specs()}

    assert names == {"get_order", "list_orders", "cancel_order", "change_address", "open_ticket"}


def test_user_id_is_never_a_tool_argument(toolbox):
    """El modelo no puede elegir en nombre de qué usuario actúa."""
    for spec in toolbox.specs():
        assert "user_id" not in spec.parameters.get("properties", {})


def test_specs_include_argument_schema(toolbox):
    specs = {s.name: s for s in toolbox.specs()}

    schema = specs["change_address"].parameters

    assert set(schema["required"]) == {"order_id", "new_address"}


# --- Validación ------------------------------------------------------------------------


def test_unknown_tool_is_rejected(toolbox):
    with pytest.raises(InvalidToolCall, match="no existe"):
        toolbox.validate(call("delete_database"))


@pytest.mark.parametrize(
    "arguments",
    [{}, {"order_id": "tres"}, {"order_id": -1}],
)
def test_invalid_arguments_are_rejected(toolbox, arguments):
    with pytest.raises(InvalidToolCall, match="order_id"):
        toolbox.validate(call("get_order", **arguments))


def test_blank_address_is_rejected(toolbox):
    with pytest.raises(InvalidToolCall, match="new_address"):
        toolbox.validate(call("change_address", order_id=1, new_address="   "))


@pytest.mark.parametrize(
    ("name", "arguments", "destructive"),
    [
        ("get_order", {"order_id": 1}, False),
        ("list_orders", {}, False),
        ("open_ticket", {"subject": "a", "description": "b"}, False),
        ("cancel_order", {"order_id": 1}, True),
        ("change_address", {"order_id": 1, "new_address": "Calle Luna 2"}, True),
    ],
)
def test_destructive_tools_are_flagged(toolbox, name, arguments, destructive):
    assert toolbox.validate(call(name, **arguments)).is_destructive is destructive


def test_confirmation_text_describes_the_action(toolbox):
    validated = toolbox.validate(call("change_address", order_id=3, new_address="Calle Luna 2"))

    assert validated.confirmation_text() == "Cambiar la dirección del pedido 3 a «Calle Luna 2»"


# --- Ejecución -------------------------------------------------------------------------


def run(toolbox, user, name, **arguments):
    return toolbox.run(user.id, toolbox.validate(call(name, **arguments)))


def test_get_order_returns_the_order_as_json(toolbox, alice, make_order):
    order = make_order(alice, status=OrderStatus.PAID)

    result = run(toolbox, alice, "get_order", order_id=order.id)

    assert result.name == "get_order"
    assert result.content["id"] == order.id
    assert result.content["status"] == "paid"


def test_tools_act_only_on_the_session_user(toolbox, alice, bob, make_order):
    """Pedido ajeno → mismo error que uno inexistente (no se revela que existe)."""
    order = make_order(bob)

    result = run(toolbox, alice, "get_order", order_id=order.id)

    assert result.content == {"error": f"Pedido {order.id} no encontrado."}


def test_list_orders_returns_only_own_orders(toolbox, alice, bob, make_order):
    mine = make_order(alice)
    make_order(bob)

    result = run(toolbox, alice, "list_orders")

    assert [o["id"] for o in result.content["orders"]] == [mine.id]


def test_business_errors_are_returned_to_the_model(toolbox, alice, make_order):
    order = make_order(alice, status=OrderStatus.SHIPPED)

    result = run(toolbox, alice, "cancel_order", order_id=order.id)

    assert "No se puede cancelar" in result.content["error"]


def test_cancel_order_runs_when_executed(toolbox, alice, make_order):
    """`run` ejecuta de verdad: por eso el bucle solo lo llama tras la confirmación."""
    order = make_order(alice, status=OrderStatus.PENDING)

    result = run(toolbox, alice, "cancel_order", order_id=order.id)

    assert result.content["status"] == "cancelled"


def test_open_ticket_creates_a_ticket(toolbox, alice, make_order):
    order = make_order(alice)

    result = run(
        toolbox,
        alice,
        "open_ticket",
        subject="Pelota rota",
        description="La pelota llegó rajada.",
        order_id=order.id,
    )

    assert result.content["subject"] == "Pelota rota"
    assert result.content["order_id"] == order.id
