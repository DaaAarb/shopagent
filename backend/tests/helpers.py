"""Utilidades compartidas por los tests (no son fixtures: se importan)."""

from app.agent.llm import LLMResponse, Message, ToolCall


def as_user(user) -> dict[str, str]:
    """Cabeceras de la autenticación simulada para actuar como `user`."""
    return {"X-User-Id": str(user.id)}


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
