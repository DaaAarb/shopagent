"""Primitivas de seguridad: hash de contraseñas y tokens de sesión (JWT).

Funciones puras, sin FastAPI ni base de datos: fáciles de probar y de reutilizar.

- Contraseñas: argon2 (vía pwdlib). Lento A PROPÓSITO y con sal aleatoria: si se
  filtrara la tabla de usuarios, adivinar cada contraseña costaría muchísimo.
- Sesión: un JWT firmado con SECRET_KEY (HS256) que dice "soy el usuario N" y
  caduca. La firma impide modificarlo: cambiar el `sub` invalida el token.
"""

from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.config import get_settings

_hasher = PasswordHash.recommended()  # argon2id con parámetros recomendados
_ALGORITHM = "HS256"

# Hash de una contraseña cualquiera. Se usa cuando el email no existe para tardar
# lo mismo que con uno real: así no se puede averiguar qué emails están registrados
# midiendo el tiempo de respuesta.
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
        "sub": str(user_id),  # el estándar JWT pide que `sub` sea texto
        "iat": now,
        "exp": now + timedelta(minutes=get_settings().session_minutes),
    }
    return jwt.encode(payload, _secret(), algorithm=_ALGORITHM)


def read_session_token(token: str) -> int:
    """Devuelve el user_id del token o lanza InvalidToken."""
    try:
        # `algorithms` explícito: evita ataques que cambian el algoritmo del token ("none").
        payload = jwt.decode(token, _secret(), algorithms=[_ALGORITHM], options={"require": ["exp", "sub"]})
        return int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError) as exc:  # incluye caducado y firma inválida
        raise InvalidToken() from exc
