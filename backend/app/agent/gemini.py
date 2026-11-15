"""Adaptador de Gemini: implementa la interfaz `LLMClient` (agent/llm.py) con Google.

Es el ÚNICO módulo que importa el SDK de Google. Traduce en los dos sentidos:
    formato del agente (Message, ToolSpec)  →  formato de Gemini  →  llamada a la API
    respuesta de Gemini                     →  LLMResponse
"""

import base64

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from app.agent.llm import LLMError, LLMResponse, Message, ToolCall, ToolSpec


class GeminiClient:
    """Cumple `LLMClient` por su forma (tiene `generate`), sin heredar de él."""

    def __init__(self, api_key: str, model: str, timeout_seconds: float = 30) -> None:
        # Sin timeout, una respuesta lenta del proveedor dejaría colgada la petición
        # /chat indefinidamente. El SDK espera el valor en milisegundos.
        self._client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=int(timeout_seconds * 1000)),
        )
        self._model = model

    def generate(
        self, system: str, history: list[Message], tools: list[ToolSpec]
    ) -> LLMResponse:
        config = types.GenerateContentConfig(
            system_instruction=system,
            tools=[to_gemini_tool(tools)] if tools else None,
            # El SDK puede ejecutar funciones Python solo. Lo desactivamos: quien
            # ejecuta (y valida, y pide confirmación) es nuestro bucle, no el SDK.
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        try:
            response = self._client.models.generate_content(
                model=self._model, contents=to_gemini_contents(history), config=config
            )
        except genai_errors.APIError as exc:
            raise LLMError(f"Gemini respondió con error {exc.code}") from exc
        return from_gemini_response(response)


# --- Traducciones (funciones puras: se prueban sin llamar a la API) ----------------


def to_gemini_tool(tools: list[ToolSpec]) -> types.Tool:
    return types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name=t.name, description=t.description, parameters_json_schema=t.parameters
            )
            for t in tools
        ]
    )


def to_gemini_contents(history: list[Message]) -> list[types.Content]:
    contents = []
    for message in history:
        if message.role == "user":
            contents.append(types.Content(role="user", parts=[types.Part(text=message.text)]))
        elif message.role == "assistant":
            parts = [types.Part(text=message.text)] if message.text else []
            parts += [
                types.Part(
                    function_call=types.FunctionCall(name=call.name, args=call.arguments),
                    # Gemini 3 exige recibir de vuelta la firma que adjuntó a la llamada.
                    thought_signature=base64.b64decode(call.signature) if call.signature else None,
                )
                for call in message.tool_calls
            ]
            # Gemini llama "model" al rol del asistente.
            contents.append(types.Content(role="model", parts=parts))
        else:  # "tool": en Gemini los resultados viajan en un turno de usuario
            contents.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_function_response(name=r.name, response=r.content)
                        for r in message.tool_results
                    ],
                )
            )
    return contents


def from_gemini_response(response: types.GenerateContentResponse) -> LLMResponse:
    if not response.candidates or response.candidates[0].content is None:
        raise LLMError("Gemini no devolvió ninguna respuesta.")

    texts: list[str] = []
    calls: list[ToolCall] = []
    for part in response.candidates[0].content.parts or []:
        if part.thought:  # razonamiento interno del modelo: no es para el usuario
            continue
        if part.function_call:
            calls.append(
                ToolCall(
                    name=part.function_call.name,
                    arguments=dict(part.function_call.args or {}),
                    signature=(
                        base64.b64encode(part.thought_signature).decode()
                        if part.thought_signature
                        else None
                    ),
                )
            )
        elif part.text:
            texts.append(part.text)

    return LLMResponse(text="".join(texts) or None, tool_calls=calls)
