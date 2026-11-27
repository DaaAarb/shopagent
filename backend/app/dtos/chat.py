from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.dtos.common import NonBlank


class ChatMessageCreate(BaseModel):
    # Acotado: el mensaje se envía al LLM y consume tokens.
    message: Annotated[NonBlank, StringConstraints(max_length=2000)]


class ChatConfirm(BaseModel):
    """Respuesta del cliente al botón "Confirmar / Cancelar" de una acción pendiente."""

    action_id: NonBlank
    approve: bool
