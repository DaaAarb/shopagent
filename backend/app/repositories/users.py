from sqlmodel import col

from app.models import User
from app.repositories.base import Repository


class UserRepository(Repository[User]):
    model = User

    def list_all(self) -> list[User]:
        return self.find(order_by=(col(User.id),))

    def get_by_email(self, email: str) -> User | None:
        found = self.find(col(User.email) == email)
        return found[0] if found else None
