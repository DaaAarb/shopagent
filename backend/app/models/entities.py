from datetime import UTC, datetime

from sqlmodel import Field, SQLModel

from app.models.enums import OrderStatus


def _utcnow() -> datetime:
    return datetime.now(UTC)


class User(SQLModel, table=True):
    """Cliente de Loba Toys. La autenticación es simulada (cabecera X-User-Id)."""

    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)


class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # Indexado: casi todas las consultas filtran por el dueño del pedido.
    user_id: int = Field(foreign_key="user.id", index=True)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    # Resumen legible de lo comprado ("Pelota de goma x2, Cuerda trenzada").
    # No hay tabla de productos: ninguna herramienta del agente la necesita.
    items: str
    # Céntimos en un entero: los float no representan bien el dinero (0.1 + 0.2 != 0.3).
    # Ojo: los modelos table=True NO validan (un Field(ge=0) aquí no haría nada).
    # La validación vive en los esquemas de entrada y en services/.
    total_cents: int
    shipping_address: str
    created_at: datetime = Field(default_factory=_utcnow)


class Ticket(SQLModel, table=True):
    """Incidencia abierta por el agente cuando no puede resolver algo (escalado a humano)."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    # Opcional: hay consultas que no son sobre un pedido concreto.
    order_id: int | None = Field(default=None, foreign_key="order.id")
    subject: str
    description: str
    created_at: datetime = Field(default_factory=_utcnow)
