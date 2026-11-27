"""Capa HTTP de /chat y /chat/confirm (la lógica del agente está en test_agent.py)."""

import pytest

from app.agent.history import InMemoryChatStore
from app.agent.llm import LLMError
from app.api.deps import get_chat_store, get_llm
from app.main import app
from app.models import OrderStatus
from tests.helpers import FakeLLM, as_user, calls, says


@pytest.fixture
def script(client):
    """Fija el guion del LLM falso para la siguiente petición: `script(says("hola"))`."""
    store = InMemoryChatStore()
    app.dependency_overrides[get_chat_store] = lambda: store

    def _script(*responses):
        llm = FakeLLM(*responses)
        app.dependency_overrides[get_llm] = lambda: llm
        return llm

    return _script


def test_chat_returns_the_agent_reply(client, script, alice):
    script(says("¡Hola, Alice!"))

    response = client.post("/chat", json={"message": "Hola"}, headers=as_user(alice))

    assert response.status_code == 200
    assert response.json() == {"reply": "¡Hola, Alice!", "pending_action": None}


def test_chat_requires_user_header(client, script):
    script(says("no debería llegar aquí"))

    assert client.post("/chat", json={"message": "Hola"}).status_code == 401


@pytest.mark.parametrize("message", ["", "   ", "x" * 2001])
def test_chat_rejects_empty_or_huge_messages(client, script, alice, message):
    script()

    response = client.post("/chat", json={"message": message}, headers=as_user(alice))

    assert response.status_code == 422


def test_full_cancel_flow_through_the_api(client, script, alice, make_order):
    order = make_order(alice, status=OrderStatus.PENDING)
    script(calls("cancel_order", order_id=order.id))

    proposal = client.post("/chat", json={"message": "Cancela"}, headers=as_user(alice)).json()
    pending = proposal["pending_action"]
    assert pending["description"] == f"Cancelar el pedido {order.id}"
    # Aún no se ha cancelado.
    assert client.get(f"/orders/{order.id}", headers=as_user(alice)).json()["status"] == "pending"

    confirm = client.post(
        "/chat/confirm",
        json={"action_id": pending["id"], "approve": True},
        headers=as_user(alice),
    )

    assert confirm.status_code == 200
    assert confirm.json()["pending_action"] is None
    assert client.get(f"/orders/{order.id}", headers=as_user(alice)).json()["status"] == "cancelled"


def test_confirming_unknown_action_is_409(client, script, alice):
    script()

    response = client.post(
        "/chat/confirm", json={"action_id": "inventado", "approve": True}, headers=as_user(alice)
    )

    assert response.status_code == 409


def test_llm_failure_is_503_without_leaking_details(client, script, alice):
    class BrokenLLM:
        def generate(self, system, history, tools):
            raise LLMError("Gemini: 500 INTERNAL secreto-interno")

    app.dependency_overrides[get_llm] = lambda: BrokenLLM()

    response = client.post("/chat", json={"message": "Hola"}, headers=as_user(alice))

    assert response.status_code == 503
    assert "secreto" not in response.text


def test_missing_api_key_is_503(client, alice, monkeypatch):
    """Sin override de get_llm: la dependencia real detecta que falta la key."""
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "gemini_api_key", "")
    app.dependency_overrides[get_chat_store] = InMemoryChatStore

    response = client.post("/chat", json={"message": "Hola"}, headers=as_user(alice))

    assert response.status_code == 503
