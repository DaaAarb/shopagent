from collections.abc import Iterator

from sqlmodel import Session, create_engine

from app.config import get_settings

# pool_pre_ping descarta conexiones caídas (p. ej. tras reiniciar PostgreSQL).
engine = create_engine(get_settings().database_url, pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    """Una sesión por petición (dependencia de FastAPI)."""
    with Session(engine) as session:
        yield session
