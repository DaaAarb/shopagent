"""Herramientas del agente: las únicas acciones que el LLM puede solicitar.

El modelo propone herramienta y argumentos; aquí se validan con Pydantic y se
ejecutan a través de la capa de servicios. El `user_id` nunca es un argumento:
sale de la sesión, así que ni un prompt injection permite actuar como otro usuario.
Las herramientas con `confirmation` son destructivas y requieren aprobación.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, Any

from pydantic import BaseModel, Field, StringConstraints, ValidationError

from app.agent.llm import ToolCall, ToolResult, ToolSpec
from app.dtos.common import NonBlank
from app.services import OrderService, ShopError, TicketService

# --- Argumentos de cada herramienta ------------------------------------------------
# Las `description` de los campos llegan al modelo dentro del JSON Schema.

OrderId = Annotated[int, Field(gt=0, description="Número del pedido, p. ej. 3.")]


class NoArgs(BaseModel):
    pass


class OrderArgs(BaseModel):
    order_id: OrderId


class ChangeAddressArgs(BaseModel):
    order_id: OrderId
    new_address: Annotated[
        NonBlank,
        StringConstraints(max_length=200),
        Field(description="Dirección de envío completa: calle, número, código postal y ciudad."),
    ]


class OpenTicketArgs(BaseModel):
    subject: Annotated[
        NonBlank, StringConstraints(max_length=120), Field(description="Resumen breve del problema.")
    ]
    description: Annotated[
        NonBlank,
        StringConstraints(max_length=2000),
        Field(description="Qué ha pasado y qué necesita el cliente, con todo el detalle útil."),
    ]
    order_id: Annotated[
        int | None, Field(gt=0, description="Pedido relacionado, si lo hay.")
    ] = None


# --- Registro de herramientas -------------------------------------------------------


@dataclass(frozen=True)
class ToolServices:
    orders: OrderService
    tickets: TicketService


@dataclass(frozen=True)
class AgentTool:
    name: str
    description: str
    args_model: type[BaseModel]
    # Recibe el user_id de la sesión, nunca uno propuesto por el modelo.
    run: Callable[[ToolServices, int, Any], dict[str, Any]]
    # Si existe, la herramienta es destructiva y requiere confirmación.
    confirmation: Callable[[Any], str] | None = None

    @property
    def is_destructive(self) -> bool:
        return self.confirmation is not None


def _dump(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(mode="json")


TOOLS: dict[str, AgentTool] = {
    tool.name: tool
    for tool in [
        AgentTool(
            name="get_order",
            description="Consulta un pedido del cliente: estado, productos, total y dirección.",
            args_model=OrderArgs,
            run=lambda s, user_id, a: _dump(s.orders.get_order(user_id, a.order_id)),
        ),
        AgentTool(
            name="list_orders",
            description="Lista todos los pedidos del cliente, del más reciente al más antiguo.",
            args_model=NoArgs,
            run=lambda s, user_id, a: {
                "orders": [_dump(o) for o in s.orders.list_orders(user_id)]
            },
        ),
        AgentTool(
            name="cancel_order",
            description=(
                "Cancela un pedido (solo si está pendiente o pagado) y repone el stock. "
                "Requiere confirmación del cliente: el sistema se la pedirá."
            ),
            args_model=OrderArgs,
            run=lambda s, user_id, a: _dump(s.orders.cancel_order(user_id, a.order_id)),
            confirmation=lambda a: f"Cancelar el pedido {a.order_id}",
        ),
        AgentTool(
            name="change_address",
            description=(
                "Cambia la dirección de envío de un pedido (solo antes de enviarse). "
                "Requiere confirmación del cliente: el sistema se la pedirá."
            ),
            args_model=ChangeAddressArgs,
            run=lambda s, user_id, a: _dump(
                s.orders.change_address(user_id, a.order_id, a.new_address)
            ),
            confirmation=lambda a: (
                f"Cambiar la dirección del pedido {a.order_id} a «{a.new_address}»"
            ),
        ),
        AgentTool(
            name="open_ticket",
            description=(
                "Abre una incidencia para que la revise una persona del equipo. Úsala cuando "
                "no puedas resolver algo con las demás herramientas o el cliente lo pida."
            ),
            args_model=OpenTicketArgs,
            run=lambda s, user_id, a: _dump(
                s.tickets.open_ticket(user_id, a.subject, a.description, a.order_id)
            ),
        ),
    ]
}


# --- Validación y ejecución ----------------------------------------------------------


class InvalidToolCall(Exception):
    """Herramienta inexistente o argumentos inválidos; el mensaje vuelve al modelo."""


@dataclass(frozen=True)
class ValidatedCall:
    tool: AgentTool
    args: BaseModel

    @property
    def is_destructive(self) -> bool:
        return self.tool.is_destructive

    def confirmation_text(self) -> str:
        assert self.tool.confirmation is not None, "Solo las destructivas se confirman"
        return self.tool.confirmation(self.args)


class ToolBox:
    def __init__(self, services: ToolServices) -> None:
        self.services = services

    def specs(self) -> list[ToolSpec]:
        return [
            ToolSpec(
                name=t.name, description=t.description, parameters=t.args_model.model_json_schema()
            )
            for t in TOOLS.values()
        ]

    def validate(self, call: ToolCall) -> ValidatedCall:
        tool = TOOLS.get(call.name)
        if tool is None:
            raise InvalidToolCall(f"La herramienta '{call.name}' no existe.")
        try:
            args = tool.args_model.model_validate(call.arguments)
        except ValidationError as exc:
            problems = "; ".join(
                f"{'.'.join(map(str, e['loc'])) or 'argumentos'}: {e['msg']}" for e in exc.errors()
            )
            raise InvalidToolCall(f"Argumentos inválidos para '{call.name}': {problems}") from exc
        return ValidatedCall(tool=tool, args=args)

    def run(self, user_id: int, call: ValidatedCall) -> ToolResult:
        """Ejecuta la herramienta; los errores de negocio se devuelven como resultado para el modelo."""
        try:
            content = call.tool.run(self.services, user_id, call.args)
        except ShopError as exc:
            content = {"error": str(exc)}
        return ToolResult(name=call.tool.name, content=content)
