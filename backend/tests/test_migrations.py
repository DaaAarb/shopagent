"""Las migraciones de Alembic deben coincidir con los modelos y ser reversibles."""

from alembic import command
from sqlalchemy import Engine

from tests.conftest import alembic_config


def test_migrations_match_models(engine: Engine):
    """Equivale a `alembic check`."""
    with engine.connect() as connection:
        command.check(alembic_config(connection))


def test_migrations_can_be_rolled_back_and_reapplied(engine: Engine):
    """downgrade base → upgrade head, dentro de una transacción que se revierte."""
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            config = alembic_config(connection)
            command.downgrade(config, "base")
            command.upgrade(config, "head")
            command.check(config)
        finally:
            transaction.rollback()
