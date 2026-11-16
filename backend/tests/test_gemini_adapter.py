"""Adaptador de Gemini (agent/gemini.py): traducciones de ida y vuelta, sin llamar a la API."""

import base64

import pytest
from google.genai import types

from app.agent.gemini import from_gemini_response, to_gemini_contents, to_gemini_tool
from app.agent.llm import LLMError, Message, ToolCall, ToolResult, ToolSpec

SIGNATURE = b"firma-opaca"


def gemini_response(*parts: types.Part) -> types.GenerateContentResponse:
    return types.GenerateContentResponse(
        candidates=[types.Candidate(content=types.Content(role="model", parts=list(parts)))]
    )


# --- Gemini → formato neutro --------------------------------------------------------


def test_text_response_is_translated():
    response = from_gemini_response(gemini_response(types.Part(text="¡Hola!")))

    assert response.text == "¡Hola!"
    assert response.tool_calls == []


def test_function_call_is_translated_with_its_signature():
    part = types.Part(
        function_call=types.FunctionCall(name="get_order", args={"order_id": 3}),
        thought_signature=SIGNATURE,
    )

    [call] = from_gemini_response(gemini_response(part)).tool_calls

    assert call.name == "get_order"
    assert call.arguments == {"order_id": 3}
    assert base64.b64decode(call.signature) == SIGNATURE


def test_internal_thoughts_are_not_shown_to_the_user():
    response = from_gemini_response(
        gemini_response(
            types.Part(text="razonamiento interno", thought=True),
            types.Part(text="Respuesta final"),
        )
    )

    assert response.text == "Respuesta final"


def test_empty_response_raises_llm_error():
    with pytest.raises(LLMError):
        from_gemini_response(types.GenerateContentResponse(candidates=[]))


# --- Formato neutro → Gemini -------------------------------------------------------


def test_history_is_translated_to_gemini_roles():
    history = [
        Message(role="user", text="¿Cómo va mi pedido 3?"),
        Message(
            role="assistant",
            tool_calls=[
                ToolCall(
                    name="get_order",
                    arguments={"order_id": 3},
                    signature=base64.b64encode(SIGNATURE).decode(),
                )
            ],
        ),
        Message(
            role="tool",
            tool_results=[ToolResult(name="get_order", content={"status": "paid"})],
        ),
        Message(role="assistant", text="Tu pedido está pagado."),
    ]

    contents = to_gemini_contents(history)

    assert [c.role for c in contents] == ["user", "model", "user", "model"]
    call_part = contents[1].parts[0]
    assert call_part.function_call.name == "get_order"
    # La firma vuelve a Gemini tal cual la mandó.
    assert call_part.thought_signature == SIGNATURE
    assert contents[2].parts[0].function_response.response == {"status": "paid"}


def test_tool_specs_become_function_declarations():
    spec = ToolSpec(
        name="get_order",
        description="Consulta un pedido.",
        parameters={"type": "object", "properties": {"order_id": {"type": "integer"}}},
    )

    [declaration] = to_gemini_tool([spec]).function_declarations

    assert declaration.name == "get_order"
    assert declaration.parameters_json_schema["properties"]["order_id"]["type"] == "integer"
