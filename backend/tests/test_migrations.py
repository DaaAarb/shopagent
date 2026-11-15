"""Las migraciones de Alembic y los modelos no deben divergir.

El fixture `engine` ya aplicó `alembic upgrade head` sobre la BD de tests.
Si alguien cambia un modelo y olvida generar la migración, estos tests fallan.
"""

from alembic import command
from sqlalchemy import Engine

from tests.conftest import alembic_config


def test_migrations_match_models(engine: Engine):
    """Equivale a `alembic check`: lanza una excepción si hay diferencias."""
    with engine.connect() as connection:
        command.check(alembic_config(connection))


def test_migrations_can_be_rolled_back_and_reapplied(engine: Engine):
    """downgrade base → upgrade head funciona (p. ej., no quedan tipos ENUM huérfanos).

    Todo ocurre en una transacción que se revierte: el esquema queda intacto
    para el resto de tests (PostgreSQL permite DDL dentro de transacciones).
    """
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            config = alembic_config(connection)
            command.downgrade(config, "base")
            command.upgrade(config, "head")
            command.check(config)
        finally:
            transaction.rollback()
