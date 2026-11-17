"""Utilidades compartidas por los tests (no son fixtures: se importan)."""

from app.agent.llm import LLMResponse, Message, ToolCall
from app.api.deps import SESSION_COOKIE
from app.security import create_session_token


def as_user(user) -> dict[str, str]:
    """Cabeceras para actuar como `user`: la cookie de sesión con un token válido.

    Equivale a haber hecho login, sin pasar por /auth/login en cada test.
    """
    return {"Cookie": f"{SESSION_COOKIE}={create_session_token(user.id)}"}


class FakeLLM:
    """LLM falso: devuelve respuestas guionizadas y apunta lo que recibió.

    Cumple la interfaz `LLMClient` sin heredar de ella (Protocol = tipado estructural).
    """

    def __init__(self, *responses: LLMResponse) -> None:
        self.responses = list(responses)
        self.received: list[list[Message]] = []  # historial recibido en cada llamada

    def generate(self, system, history, tools) -> LLMResponse:
        self.received.append(list(history))
        return self.responses.pop(0)


def says(text: str) -> LLMResponse:
    return LLMResponse(text=text)


def calls(name: str, **arguments) -> LLMResponse:
    return LLMResponse(tool_calls=[ToolCall(name=name, arguments=arguments)])
