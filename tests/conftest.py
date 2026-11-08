from collections.abc import Iterator

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401  (registra las tablas)
from app.db.session import enable_sqlite_foreign_keys


@pytest.fixture
def session() -> Iterator[Session]:
    """Base de datos SQLite en memoria, nueva y vacía para cada test.

    StaticPool reutiliza una única conexión: con SQLite en memoria, cada
    conexión nueva sería una base de datos distinta (y vacía).
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    enable_sqlite_foreign_keys(engine)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()
