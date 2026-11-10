from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.routes import orders, tickets, users
from app.db.session import create_db_and_tables


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Al arrancar, crea las tablas que falten (en producción se usarían migraciones)."""
    create_db_and_tables()
    yield


app = FastAPI(
    title="ShopAgent",
    description="API de Loba Toys: pedidos y tickets, con reglas de negocio en el backend.",
    version="0.1.0-dev",
    lifespan=lifespan,
)

register_exception_handlers(app)
app.include_router(users.router)
app.include_router(orders.router)
app.include_router(tickets.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Comprobación de vida: la usarán Docker y el despliegue."""
    return {"status": "ok"}
