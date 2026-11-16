from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.routes import chat, demo, orders, products, tickets, users

# El esquema de la BD lo crean las migraciones (`alembic upgrade head`), no la app.
app = FastAPI(
    title="ShopAgent",
    description="API de Loba Toys: pedidos y tickets, con reglas de negocio en el backend.",
    version="0.1.0-dev",
)

register_exception_handlers(app)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(tickets.router)
app.include_router(chat.router)
app.include_router(demo.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Comprobación de vida: la usarán Docker y el despliegue."""
    return {"status": "ok"}
