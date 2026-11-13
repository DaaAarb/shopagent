from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from app.dtos.common import NonBlank

# --- Entrada --------------------------------------------------------------------


class TicketCreate(BaseModel):
    subject: Annotated[NonBlank, StringConstraints(max_length=120)]
    description: Annotated[NonBlank, StringConstraints(max_length=2000)]
    order_id: int | None = None


# --- Salida ---------------------------------------------------------------------


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int | None
    subject: str
    description: str
    created_at: datetime
