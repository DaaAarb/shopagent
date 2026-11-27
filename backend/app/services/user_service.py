from app.dtos import UserRead
from app.repositories import UnitOfWork
from app.services.exceptions import UserNotFound


class UserService:

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def get_user(self, user_id: int) -> UserRead:
        user = self.uow.users.get(user_id)
        if user is None:
            raise UserNotFound(user_id)
        return UserRead.model_validate(user)
