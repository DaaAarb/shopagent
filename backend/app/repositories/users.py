from sqlmodel import col

from app.models import User
from app.repositories.base import Repository


class UserRepository(Repository[User]):
    model = User

    def list_all(self) -> list[User]:
        return self.find(order_by=(col(User.id),))
