from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.dtos.common import NonBlank

# Validación de forma básica (algo@algo.algo) y normalizado a minúsculas:
# "Lucia@Example.com" y "lucia@example.com" son la misma cuenta.
Email = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, to_lower=True, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    ),
]


class RegisterRequest(BaseModel):
    name: Annotated[NonBlank, StringConstraints(max_length=100)]
    email: Email
    # Mínimo 8 (recomendación NIST); máximo para no hashear textos enormes.
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]


class LoginRequest(BaseModel):
    email: Email
    # Sin mínimo: una contraseña corta simplemente no coincidirá.
    password: Annotated[str, StringConstraints(max_length=128)]
