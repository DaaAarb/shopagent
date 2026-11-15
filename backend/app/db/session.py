from collections.abc import Iterator

from sqlmodel import Session, create_engine

from app.config import get_settings

# El esquema no se crea aquí: lo gestionan las migraciones (`alembic upgrade head`).
# pool_pre_ping descarta conexiones caídas (p. ej. si se reinicia PostgreSQL).
engine = create_engine(get_settings().database_url, pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    """Abre una sesión por petición y la cierra al terminar.

    En la API se usa como dependencia de FastAPI: `Depends(get_session)`.
    """
    with Session(engine) as session:
        yield session
