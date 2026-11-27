"""Historial del chat y acción pendiente por usuario: Redis con TTL y una versión en memoria para tests."""

from typing import Protocol

from pydantic import BaseModel, TypeAdapter
from redis import Redis

from app.agent.llm import Message, ToolCall

# También acota el contexto que se envía al modelo en cada turno.
MAX_HISTORY_MESSAGES = 30

_messages = TypeAdapter(list[Message])


class PendingAction(BaseModel):
    """Acción destructiva propuesta por el modelo, pendiente de confirmación."""

    id: str  # la confirmación debe referirse a esta acción concreta
    tool_call: ToolCall
    description: str


class ChatStore(Protocol):
    def load_history(self, user_id: int) -> list[Message]: ...
    def save_history(self, user_id: int, history: list[Message]) -> None: ...
    def get_pending(self, user_id: int) -> PendingAction | None: ...
    def set_pending(self, user_id: int, action: PendingAction | None) -> None: ...


def trim_history(history: list[Message], limit: int = MAX_HISTORY_MESSAGES) -> list[Message]:
    """Últimos `limit` mensajes, empezando siempre en uno del usuario.

    Un corte arbitrario podría dejar un resultado de herramienta sin su llamada,
    y el proveedor rechazaría el historial.
    """
    if len(history) <= limit:
        return history
    tail = history[-limit:]
    for index, message in enumerate(tail):
        if message.role == "user":
            return tail[index:]
    return []


class RedisChatStore:
    def __init__(self, redis: Redis, ttl_seconds: int) -> None:
        self.redis = redis
        self.ttl = ttl_seconds

    def load_history(self, user_id: int) -> list[Message]:
        raw = self.redis.get(f"chat:{user_id}:history")
        return _messages.validate_json(raw) if raw else []

    def save_history(self, user_id: int, history: list[Message]) -> None:
        # Cada escritura renueva el TTL.
        self.redis.set(
            f"chat:{user_id}:history", _messages.dump_json(trim_history(history)), ex=self.ttl
        )

    def get_pending(self, user_id: int) -> PendingAction | None:
        raw = self.redis.get(f"chat:{user_id}:pending")
        return PendingAction.model_validate_json(raw) if raw else None

    def set_pending(self, user_id: int, action: PendingAction | None) -> None:
        key = f"chat:{user_id}:pending"
        if action is None:
            self.redis.delete(key)
        else:
            self.redis.set(key, action.model_dump_json(), ex=self.ttl)


class InMemoryChatStore:
    """Implementación para tests. Guarda JSON, como Redis, para no compartir referencias."""

    def __init__(self) -> None:
        self._history: dict[int, str] = {}
        self._pending: dict[int, str] = {}

    def load_history(self, user_id: int) -> list[Message]:
        raw = self._history.get(user_id)
        return _messages.validate_json(raw) if raw else []

    def save_history(self, user_id: int, history: list[Message]) -> None:
        self._history[user_id] = _messages.dump_json(trim_history(history)).decode()

    def get_pending(self, user_id: int) -> PendingAction | None:
        raw = self._pending.get(user_id)
        return PendingAction.model_validate_json(raw) if raw else None

    def set_pending(self, user_id: int, action: PendingAction | None) -> None:
        if action is None:
            self._pending.pop(user_id, None)
        else:
            self._pending[user_id] = action.model_dump_json()
