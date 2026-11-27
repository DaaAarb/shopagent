from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import DogSize, OrderStatus, ProductCategory

# Los modelos table=True no validan al instanciarse: la validación vive en los DTOs
# y en services/. Los importes van en céntimos (int).


def _utcnow() -> datetime:
    return datetime.now(UTC)


class User(SQLModel, table=True):
    """Cliente de Loba Toys."""

    id: int | None = Field(default=None, primary_key=True)
    name: str
    # En minúsculas: lo normaliza el DTO de entrada.
    email: str = Field(unique=True, index=True)
    # Ningún DTO de salida lo expone.
    password_hash: str


class Product(SQLModel, table=True):
    """Juguete del catálogo (máximo 8). Sin tallas ni variantes."""

    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True)
    name: str
    category: ProductCategory
    description: str
    price_cents: int
    stock: int
    material: str
    dog_size: DogSize
    image_url: str | None = None
    model_url: str | None = None


class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    # Persistido: el histórico no depende del catálogo.
    total_cents: int
    shipping_address: str
    created_at: datetime = Field(default_factory=_utcnow, sa_type=DateTime(timezone=True))

    items: list["OrderItem"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    """Línea de pedido: qué producto, cuántas unidades y a qué precio."""

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", index=True)
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    # Copiado del producto al comprar: los pedidos antiguos conservan lo que se pagó.
    unit_price_cents: int

    order: Order | None = Relationship(back_populates="items")
    product: Product | None = Relationship()


class Ticket(SQLModel, table=True):
    """Incidencia abierta por el agente cuando no puede resolver algo (escalado a humano)."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    order_id: int | None = Field(default=None, foreign_key="order.id")
    subject: str
    description: str
    created_at: datetime = Field(default_factory=_utcnow, sa_type=DateTime(timezone=True))
