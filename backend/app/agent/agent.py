"""Bucle del agente: conversación con el LLM, herramientas y confirmaciones.

En cada turno, las herramientas que pide el modelo se validan. Las no destructivas
se ejecutan y su resultado vuelve al modelo; una destructiva no se ejecuta: queda
como acción pendiente hasta que el cliente la apruebe con `confirm()`. El número de
iteraciones está acotado por MAX_STEPS.
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
    id: str
    description: str


class ChatReply(BaseModel):
    reply: str
    pending_action: PendingActionRead | None = None


class NoPendingAction(Exception):
    """La acción a confirmar no existe, ha caducado o no es la actual."""


class Agent:
    def __init__(self, llm: LLMClient, tools: ToolBox, store: ChatStore) -> None:
        self.llm = llm
        self.tools = tools
        self.store = store

    def chat(self, user_id: int, text: str) -> ChatReply:
        history = self.store.load_history(user_id)
        # Un mensaje nuevo descarta la acción que esperaba confirmación.
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
                # El texto de confirmación lo genera el backend, no el LLM.
                reply = f"{pending.description}. ¿Lo confirmas?"
                history.append(Message(role="assistant", text=reply))
                self.store.set_pending(user_id, pending)
                self.store.save_history(user_id, history)
                return ChatReply(
                    reply=reply,
                    pending_action=PendingActionRead(id=pending.id, description=pending.description),
                )

        history.append(Message(role="assistant", text=FALLBACK_REPLY))
        self.store.save_history(user_id, history)
        return ChatReply(reply=FALLBACK_REPLY)

    def confirm(self, user_id: int, action_id: str, approve: bool) -> ChatReply:
        pending = self.store.get_pending(user_id)
        if pending is None or pending.id != action_id:
            raise NoPendingAction()
        # Se borra antes de ejecutar para que un doble clic no la ejecute dos veces.
        self.store.set_pending(user_id, None)

        if approve:
            # El servicio revalida las reglas: el pedido puede haber cambiado entretanto.
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

        # Queda en el historial para que el modelo tenga contexto en los turnos siguientes.
        history = self.store.load_history(user_id)
        history += [Message(role="user", text=user_text), Message(role="assistant", text=reply)]
        self.store.save_history(user_id, history)
        return ChatReply(reply=reply)

    def _handle_tool_calls(
        self, user_id: int, calls: list[ToolCall]
    ) -> tuple[list[ToolResult], PendingAction | None]:
        """Ejecuta las no destructivas y aparta como mucho una destructiva."""
        results: list[ToolResult] = []
        pending: PendingAction | None = None

        for call in calls:
            try:
                validated = self.tools.validate(call)
            except InvalidToolCall as exc:
                # El error vuelve al modelo para que corrija la llamada.
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
                # Una sola confirmación por turno.
                results.append(
                    ToolResult(
                        name=call.name,
                        content={"error": "Solo se puede confirmar una acción a la vez."},
                    )
                )
        return results, pending
