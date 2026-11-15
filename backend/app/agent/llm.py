"""Interfaz del LLM: el contrato entre el agente y cualquier proveedor.

Aquí solo hay tipos neutros y la interfaz `LLMClient`; nada de Google ni de
ningún otro proveedor. El bucle del agente depende únicamente de este módulo:
- en producción recibe un `GeminiClient` (ver agent/gemini.py);
- en los tests, un LLM falso (sin red, sin key, sin coste);
- cambiar de proveedor = escribir otra clase con el mismo `generate`.
"""

from typing import Any, Literal, Protocol

from pydantic import BaseModel


class ToolSpec(BaseModel):
    """Una herramienta tal y como se le describe al modelo."""

    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema de los argumentos


class ToolCall(BaseModel):
    """El modelo pide usar una herramienta (aún no se ha ejecutado nada)."""

    name: str
    arguments: dict[str, Any]
    # Dato opaco que algunos proveedores (Gemini 3) adjuntan a cada llamada y exigen
    # recibir de vuelta en el historial. Para el agente es una caja negra: solo lo
    # guarda y lo devuelve. En base64 para poder serializarlo en Redis.
    signature: str | None = None


class ToolResult(BaseModel):
    """Lo que devolvió la herramienta, para enseñárselo al modelo."""

    name: str
    content: dict[str, Any]


class Message(BaseModel):
    """Un turno de la conversación. Un único tipo para serializarlo fácil (JSON)."""

    role: Literal["user", "assistant", "tool"]
    text: str | None = None
    tool_calls: list[ToolCall] = []  # solo en role="assistant"
    tool_results: list[ToolResult] = []  # solo en role="tool"


class LLMResponse(BaseModel):
    """Respuesta del modelo: texto para el usuario y/o herramientas que quiere usar."""

    text: str | None = None
    tool_calls: list[ToolCall] = []


class LLMError(Exception):
    """El proveedor falló (red, timeout, cuota agotada, key inválida…)."""


class LLMClient(Protocol):
    """Interfaz: cualquier clase con este método sirve como LLM del agente.

    `Protocol` define la interfaz por su forma: no hay que heredar de ella.
    Quien la implemente solo traduce y llama; no ejecuta herramientas, no
    comprueba permisos ni pide confirmaciones (eso es del bucle del agente).
    """

    def generate(
        self, system: str, history: list[Message], tools: list[ToolSpec]
    ) -> LLMResponse: ...
