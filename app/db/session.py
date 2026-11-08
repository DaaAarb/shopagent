from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings

settings = get_settings()

# SQLite, por defecto, solo deja usar una conexión desde el hilo que la creó.
# FastAPI atiende peticiones en varios hilos, así que desactivamos esa comprobación.
# PostgreSQL no necesita este argumento.
_connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(settings.database_url, connect_args=_connect_args)


def create_db_and_tables() -> None:
    """Crea las tablas de todos los modelos importados (si no existen)."""
    import app.models  # noqa: F401  (registra los modelos en SQLModel.metadata)

    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """Abre una sesión por petición y la cierra al terminar.

    En la API se usará como dependencia de FastAPI: `Depends(get_session)`.
    """
    with Session(engine) as session:
        yield session
