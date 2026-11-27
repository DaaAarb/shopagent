"""Adaptador de Gemini para `LLMClient`. Es el único módulo que importa el SDK de Google."""

import base64

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from app.agent.llm import LLMError, LLMResponse, Message, ToolCall, ToolSpec


class GeminiClient:
    def __init__(self, api_key: str, model: str, timeout_seconds: float = 30) -> None:
        # El SDK espera el timeout en milisegundos.
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
            # Las herramientas las valida y ejecuta el bucle del agente, nunca el SDK.
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        try:
            response = self._client.models.generate_content(
                model=self._model, contents=to_gemini_contents(history), config=config
            )
        except genai_errors.APIError as exc:
            raise LLMError(f"Gemini respondió con error {exc.code}") from exc
        return from_gemini_response(response)


# --- Traducción entre los tipos del agente y los de Gemini -----------------------


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
                    # Gemini 3 exige recibir de vuelta la firma de cada llamada.
                    thought_signature=base64.b64decode(call.signature) if call.signature else None,
                )
                for call in message.tool_calls
            ]
            contents.append(types.Content(role="model", parts=parts))
        else:  # en Gemini, los resultados de herramientas van en un turno "user"
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
        if part.thought:
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
