from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración leída de variables de entorno (o del archivo .env).

    Nada sensible vive en el código: los valores por defecto apuntan al
    PostgreSQL local de `docker compose up -d db`; en otros entornos se
    sobrescriben con DATABASE_URL y TEST_DATABASE_URL.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Valores por defecto = los del docker-compose.yml (solo para desarrollo local).
    database_url: str = "postgresql+psycopg://darb:shopagent123@localhost:5433/shopagentPG"
    # Base de datos aparte para los tests: se vacía y se recrea en cada ejecución.
    test_database_url: str = (
        "postgresql+psycopg://darb:shopagent123@localhost:5433/shopagent_test"
    )

    # --- Agente ---
    # Vacía por defecto: la app arranca sin ella (el catálogo y los pedidos funcionan);
    # solo /chat la necesita. Nunca en el código: va en .env.
    gemini_api_key: str = ""
    llm_model: str = "gemini-3.5-flash"

    # Historial del chat (Redis de `docker compose up -d redis`).
    redis_url: str = "redis://localhost:6380/0"
    # La conversación se olvida tras 24 h sin actividad.
    chat_ttl_seconds: int = 24 * 60 * 60


@lru_cache
def get_settings() -> Settings:
    """Devuelve siempre la misma instancia (se lee el entorno una sola vez)."""
    return Settings()
