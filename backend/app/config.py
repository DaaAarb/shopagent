from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración leída de variables de entorno o de `.env`.

    Los valores por defecto apuntan a los servicios locales de docker-compose.yml.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://darb:shopagent123@localhost:5433/shopagentPG"
    # Los tests la vacían y la recrean en cada ejecución.
    test_database_url: str = (
        "postgresql+psycopg://darb:shopagent123@localhost:5433/shopagent_test"
    )

    # --- Autenticación ---
    # Sin valor por defecto: con un secreto conocido se podrían falsificar sesiones.
    secret_key: str = ""
    session_minutes: int = 60
    # True en producción: la cookie solo viaja por HTTPS.
    cookie_secure: bool = False

    # --- Agente ---
    # Solo la necesita /chat: el resto de la API funciona sin ella.
    gemini_api_key: str = ""
    llm_model: str = "gemini-3.5-flash"

    redis_url: str = "redis://localhost:6380/0"
    # Caducidad del historial del chat sin actividad.
    chat_ttl_seconds: int = 24 * 60 * 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
