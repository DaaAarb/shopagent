from app.dtos import UserRead
from app.repositories import UnitOfWork
from app.services.exceptions import UserNotFound


class UserService:
    """Consulta de usuarios. Con la autenticación simulada, sirve para
    comprobar que el `X-User-Id` recibido corresponde a alguien real."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def get_user(self, user_id: int) -> UserRead:
        user = self.uow.users.get(user_id)
        if user is None:
            raise UserNotFound(user_id)
        return UserRead.model_validate(user)

    def list_users(self) -> list[UserRead]:
        """Para el selector de usuario de la demo (no habría esto con login real)."""
        return [UserRead.model_validate(u) for u in self.uow.users.list_all()]
