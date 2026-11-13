from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración leída de variables de entorno (o del archivo .env).

    Nada sensible vive en el código: los valores por defecto apuntan al
    PostgreSQL local de `docker compose up -d db`; en otros entornos se
    sobrescriben con DATABASE_URL y TEST_DATABASE_URL.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://shopagent:shopagent@localhost:5433/shopagent"
    # Base de datos aparte para los tests: se vacía y se recrea en cada ejecución.
    test_database_url: str = (
        "postgresql+psycopg://shopagent:shopagent@localhost:5433/shopagent_test"
    )


@lru_cache
def get_settings() -> Settings:
    """Devuelve siempre la misma instancia (se lee el entorno una sola vez)."""
    return Settings()
