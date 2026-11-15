from fastapi import APIRouter

from app.api.deps import UserServiceDep
from app.dtos import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(users: UserServiceDep):
    """Usuarios de la demo, para el selector de la interfaz (sin login real)."""
    return users.list_users()
