"""Utilidades compartidas por los tests."""

from app.agent.llm import LLMResponse, Message, ToolCall
from app.api.deps import SESSION_COOKIE
from app.security import create_session_token


def as_user(user) -> dict[str, str]:
    """Cabecera con una cookie de sesión válida para `user`."""
    return {"Cookie": f"{SESSION_COOKIE}={create_session_token(user.id)}"}


class FakeLLM:
    """LLM falso: devuelve respuestas predefinidas y registra el historial recibido."""

    def __init__(self, *responses: LLMResponse) -> None:
        self.responses = list(responses)
        self.received: list[list[Message]] = []

    def generate(self, system, history, tools) -> LLMResponse:
        self.received.append(list(history))
        return self.responses.pop(0)


def says(text: str) -> LLMResponse:
    return LLMResponse(text=text)


def calls(name: str, **arguments) -> LLMResponse:
    return LLMResponse(tool_calls=[ToolCall(name=name, arguments=arguments)])
