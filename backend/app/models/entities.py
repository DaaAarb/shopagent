from datetime import UTC, datetime

from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import DogSize, OrderStatus, ProductCategory

# Nota: los modelos table=True NO validan al crearse (un Field(ge=0) no haría nada).
# La validación vive en los esquemas de entrada (api/) y en services/.
# El dinero siempre en céntimos (int): los float no representan bien el dinero.


def _utcnow() -> datetime:
    return datetime.now(UTC)


class User(SQLModel, table=True):
    """Cliente de Loba Toys. La autenticación es simulada (cabecera X-User-Id)."""

    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)


class Product(SQLModel, table=True):
    """Juguete del catálogo (máximo 8). Sin tallas ni variantes."""

    id: int | None = Field(default=None, primary_key=True)
    # Identificador legible para URLs: /products/pelota-saltarina
    slug: str = Field(unique=True, index=True)
    name: str
    category: ProductCategory
    description: str
    price_cents: int
    stock: int
    material: str
    dog_size: DogSize
    image_url: str | None = None
    # Modelo 3D opcional (.glb); no todos los juguetes lo tienen.
    model_url: str | None = None


class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # Indexado: casi todas las consultas filtran por el dueño del pedido.
    user_id: int = Field(foreign_key="user.id", index=True)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    # Se guarda (no solo se calcula) para que el histórico no cambie nunca.
    total_cents: int
    shipping_address: str
    created_at: datetime = Field(default_factory=_utcnow)

    items: list["OrderItem"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    """Línea de pedido: qué producto, cuántas unidades y a qué precio."""

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", index=True)
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    # Precio copiado del producto al comprar: si el catálogo cambia de precio
    # mañana, los pedidos antiguos siguen mostrando lo que se pagó.
    unit_price_cents: int

    order: Order | None = Relationship(back_populates="items")
    product: Product | None = Relationship()


class Ticket(SQLModel, table=True):
    """Incidencia abierta por el agente cuando no puede resolver algo (escalado a humano)."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    # Opcional: hay consultas que no son sobre un pedido concreto.
    order_id: int | None = Field(default=None, foreign_key="order.id")
    subject: str
    description: str
    created_at: datetime = Field(default_factory=_utcnow)
