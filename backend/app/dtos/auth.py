from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.dtos.common import NonBlank

# Validación de forma básica y normalizado a minúsculas (un email, una cuenta).
Email = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, to_lower=True, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    ),
]


class RegisterRequest(BaseModel):
    name: Annotated[NonBlank, StringConstraints(max_length=100)]
    email: Email
    # Mínimo 8 (NIST SP 800-63B); el máximo evita hashear entradas enormes.
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]


class LoginRequest(BaseModel):
    email: Email
    password: Annotated[str, StringConstraints(max_length=128)]
