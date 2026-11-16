"""Bucle del agente: conversación con el LLM, herramientas y confirmaciones.

Un turno de chat:
    1. Se añade el mensaje del cliente al historial.
    2. Se le pasa al LLM el historial y las herramientas.
    3. Si responde con texto → fin del turno.
       Si pide herramientas → se validan:
         - lectura (consultar, abrir ticket): se ejecutan y el resultado vuelve al LLM;
         - destructivas (cancelar, cambiar dirección): NO se ejecutan. Se guardan como
           acción pendiente y el turno termina preguntando al cliente si confirma.
    4. Se repite como mucho MAX_STEPS veces (evita bucles infinitos y gasto sin control).

La acción pendiente solo se ejecuta con `confirm()`, que llama el endpoint del
botón "Confirmar" del frontend. El LLM no puede confirmar nada por su cuenta.
"""

import uuid

from pydantic import BaseModel

from app.agent.history import ChatStore, PendingAction
from app.agent.llm import LLMClient, Message, ToolCall, ToolResult
from app.agent.prompt import SYSTEM_PROMPT
from app.agent.tools import InvalidToolCall, ToolBox

MAX_STEPS = 5

FALLBACK_REPLY = (
    "Lo siento, no he podido completar tu petición. ¿Puedes reformularla, "
    "o prefieres que abra una incidencia para que te ayude una persona?"
)


class PendingActionRead(BaseModel):
    """Lo que ve el frontend de una acción pendiente (para pintar el botón)."""

    id: str
    description: str


class ChatReply(BaseModel):
    reply: str
    pending_action: PendingActionRead | None = None


class NoPendingAction(Exception):
    """Se intenta confirmar una acción que no existe, ya caducó o no es la actual."""


class Agent:
    def __init__(self, llm: LLMClient, tools: ToolBox, store: ChatStore) -> None:
        # Las tres piezas se inyectan: en los tests, un LLM falso y un historial en memoria.
        self.llm = llm
        self.tools = tools
        self.store = store

    def chat(self, user_id: int, text: str) -> ChatReply:
        history = self.store.load_history(user_id)
        # Un mensaje nuevo deja sin efecto la acción que estuviera esperando
        # confirmación: el cliente ha cambiado de tema o de idea.
        self.store.set_pending(user_id, None)
        history.append(Message(role="user", text=text))

        for _ in range(MAX_STEPS):
            response = self.llm.generate(SYSTEM_PROMPT, history, self.tools.specs())
            history.append(
                Message(role="assistant", text=response.text, tool_calls=response.tool_calls)
            )
            if not response.tool_calls:
                self.store.save_history(user_id, history)
                return ChatReply(reply=response.text or FALLBACK_REPLY)

            results, pending = self._handle_tool_calls(user_id, response.tool_calls)
            history.append(Message(role="tool", tool_results=results))

            if pending is not None:
                # La pregunta de confirmación la escribe el backend, no el LLM: así el
                # cliente ve exactamente qué se va a hacer, sin interpretaciones.
                reply = f"{pending.description}. ¿Lo confirmas?"
                history.append(Message(role="assistant", text=reply))
                self.store.set_pending(user_id, pending)
                self.store.save_history(user_id, history)
                return ChatReply(
                    reply=reply,
                    pending_action=PendingActionRead(id=pending.id, description=pending.description),
                )

        # Se agotaron las vueltas sin una respuesta final.
        history.append(Message(role="assistant", text=FALLBACK_REPLY))
        self.store.save_history(user_id, history)
        return ChatReply(reply=FALLBACK_REPLY)

    def confirm(self, user_id: int, action_id: str, approve: bool) -> ChatReply:
        pending = self.store.get_pending(user_id)
        if pending is None or pending.id != action_id:
            raise NoPendingAction()
        # Se borra ANTES de ejecutar: un doble clic no puede ejecutar la acción dos veces.
        self.store.set_pending(user_id, None)

        if approve:
            # Se vuelve a validar y, al ejecutar, el servicio vuelve a comprobar las
            # reglas: el pedido puede haber cambiado de estado mientras tanto.
            result = self.tools.run(user_id, self.tools.validate(pending.tool_call))
            error = result.content.get("error")
            reply = (
                f"No he podido completarlo: {error}"
                if error
                else f"Hecho: {pending.description[0].lower()}{pending.description[1:]}."
            )
            user_text = f"Confirmo: {pending.description}"
        else:
            reply = "De acuerdo, no he hecho ningún cambio."
            user_text = f"No confirmo: {pending.description}"

        # Se anota en el historial para que el modelo sepa qué pasó en los turnos siguientes.
        history = self.store.load_history(user_id)
        history += [Message(role="user", text=user_text), Message(role="assistant", text=reply)]
        self.store.save_history(user_id, history)
        return ChatReply(reply=reply)

    def _handle_tool_calls(
        self, user_id: int, calls: list[ToolCall]
    ) -> tuple[list[ToolResult], PendingAction | None]:
        """Ejecuta las de lectura y aparta (como mucho) una destructiva."""
        results: list[ToolResult] = []
        pending: PendingAction | None = None

        for call in calls:
            try:
                validated = self.tools.validate(call)
            except InvalidToolCall as exc:
                # El modelo se equivocó: se le devuelve el error para que corrija.
                results.append(ToolResult(name=call.name, content={"error": str(exc)}))
                continue

            if not validated.is_destructive:
                results.append(self.tools.run(user_id, validated))
            elif pending is None:
                pending = PendingAction(
                    id=uuid.uuid4().hex,
                    tool_call=call,
                    description=validated.confirmation_text(),
                )
                results.append(
                    ToolResult(
                        name=call.name,
                        content={
                            "status": "pending_confirmation",
                            "detail": "NO se ha ejecutado: el cliente debe confirmarlo.",
                        },
                    )
                )
            else:
                # Una sola confirmación por turno: el cliente decide de una en una.
                results.append(
                    ToolResult(
                        name=call.name,
                        content={"error": "Solo se puede confirmar una acción a la vez."},
                    )
                )
        return results, pending
