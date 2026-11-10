from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración leída de variables de entorno (o del archivo .env).

    Nada sensible vive en el código: cambiar de SQLite a PostgreSQL
    es cambiar DATABASE_URL, sin tocar una línea de Python.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./shopagent.db"


@lru_cache
def get_settings() -> Settings:
    """Devuelve siempre la misma instancia (se lee el entorno una sola vez)."""
    return Settings()
