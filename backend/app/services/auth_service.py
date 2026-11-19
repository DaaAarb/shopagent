from sqlalchemy.exc import IntegrityError

from app.dtos import LoginRequest, RegisterRequest, UserRead
from app.models import User
from app.repositories import UnitOfWork
from app.security import hash_password, verify_password
from app.services.exceptions import EmailAlreadyRegistered, InvalidCredentials


class AuthService:
    """Registro y comprobación de credenciales.

    No sabe nada de cookies ni de tokens: eso es cosa de la capa HTTP (api/).
    Así, el día que haga falta otro mecanismo de sesión, este servicio no cambia.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def register(self, data: RegisterRequest) -> UserRead:
        if self.uow.users.get_by_email(data.email) is not None:
            raise EmailAlreadyRegistered()
        try:
            with self.uow:
                user = self.uow.users.add(
                    User(name=data.name, email=data.email, password_hash=hash_password(data.password))
                )
                self.uow.commit()
                return UserRead.model_validate(user)
        except IntegrityError as exc:
            # Dos registros simultáneos con el mismo email: la restricción UNIQUE
            # de la BD es la que manda (la comprobación de arriba no basta sola).
            raise EmailAlreadyRegistered() from exc

    def authenticate(self, data: LoginRequest) -> UserRead:
        user = self.uow.users.get_by_email(data.email)
        # Se verifica SIEMPRE (también si el usuario no existe): mismo tiempo de respuesta.
        if not verify_password(data.password, user.password_hash if user else None) or user is None:
            raise InvalidCredentials()
        return UserRead.model_validate(user)
