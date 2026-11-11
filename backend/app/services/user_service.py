from collections.abc import Sequence

from sqlmodel import Session, select

from app.models import User
from app.services.exceptions import UserNotFound


class UserService:
    """Consulta de usuarios. Con la autenticación simulada, sirve para
    comprobar que el `X-User-Id` recibido corresponde a alguien real."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_user(self, user_id: int) -> User:
        user = self.session.get(User, user_id)
        if user is None:
            raise UserNotFound(user_id)
        return user

    def list_users(self) -> Sequence[User]:
        """Para el selector de usuario de la demo (no habría esto con login real)."""
        return self.session.exec(select(User).order_by(User.id)).all()
