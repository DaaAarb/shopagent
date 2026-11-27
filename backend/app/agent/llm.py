"""Interfaz del LLM y tipos neutros, independientes del proveedor.

El bucle del agente solo depende de este módulo: en producción recibe un
`GeminiClient` y en los tests un LLM falso.
"""

from typing import Any, Literal, Protocol

from pydantic import BaseModel


class ToolSpec(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema de los argumentos


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any]
    # Dato opaco que algunos proveedores (Gemini 3) exigen recibir de vuelta en el
    # historial. En base64 para poder serializarlo.
    signature: str | None = None


class ToolResult(BaseModel):
    name: str
    content: dict[str, Any]


class Message(BaseModel):
    """Un turno de la conversación."""

    role: Literal["user", "assistant", "tool"]
    text: str | None = None
    tool_calls: list[ToolCall] = []  # solo en role="assistant"
    tool_results: list[ToolResult] = []  # solo en role="tool"


class LLMResponse(BaseModel):
    text: str | None = None
    tool_calls: list[ToolCall] = []


class LLMError(Exception):
    """Fallo del proveedor (red, timeout, cuota, credenciales…)."""


class LLMClient(Protocol):
    """Solo traduce y llama al proveedor: no ejecuta herramientas ni comprueba permisos."""

    def generate(
        self, system: str, history: list[Message], tools: list[ToolSpec]
    ) -> LLMResponse: ...
