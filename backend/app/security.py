"""Hash de contraseñas (argon2id) y tokens de sesión (JWT HS256 firmado con SECRET_KEY)."""

from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.config import get_settings

_hasher = PasswordHash.recommended()
_ALGORITHM = "HS256"

# Se verifica contra este hash cuando el usuario no existe, para que el tiempo de
# respuesta no revele qué emails están registrados.
_DUMMY_HASH = _hasher.hash("contraseña-de-relleno")


class InvalidToken(Exception):
    """Token ausente, manipulado, caducado o mal formado."""


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    """False si no hay hash (usuario inexistente o sin contraseña), tardando lo mismo."""
    matches = _hasher.verify(password, password_hash or _DUMMY_HASH)
    return matches and bool(password_hash)


def _secret() -> str:
    secret = get_settings().secret_key
    if not secret:
        raise RuntimeError("Falta SECRET_KEY en el .env (ver .env.example).")
    return secret


def create_session_token(user_id: int) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),  # RFC 7519: `sub` es una cadena
        "iat": now,
        "exp": now + timedelta(minutes=get_settings().session_minutes),
    }
    return jwt.encode(payload, _secret(), algorithm=_ALGORITHM)


def read_session_token(token: str) -> int:
    """Devuelve el user_id del token o lanza InvalidToken."""
    try:
        # Algoritmo fijado: evita ataques de confusión de algoritmo (p. ej. "none").
        payload = jwt.decode(token, _secret(), algorithms=[_ALGORITHM], options={"require": ["exp", "sub"]})
        return int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError) as exc:
        raise InvalidToken() from exc
