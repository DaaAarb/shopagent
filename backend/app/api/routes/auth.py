"""Registro, login y logout con el JWT de sesión en una cookie.

- HttpOnly: inaccesible desde JavaScript (un XSS no puede robar la sesión).
- SameSite=Lax: no se envía en POST desde otros sitios (mitiga CSRF).
- Secure en producción y Max-Age igual a la caducidad del token.
"""

from fastapi import APIRouter, Response, status

from app.api.deps import SESSION_COOKIE, AuthServiceDep, CurrentUserId, UserServiceDep
from app.config import get_settings
from app.dtos import LoginRequest, RegisterRequest, UserRead
from app.security import create_session_token

router = APIRouter(prefix="/auth", tags=["auth"])


def _start_session(response: Response, user_id: int) -> None:
    settings = get_settings()
    response.set_cookie(
        SESSION_COOKIE,
        create_session_token(user_id),
        max_age=settings.session_minutes * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, response: Response, auth: AuthServiceDep):
    """Crea la cuenta e inicia sesión directamente."""
    user = auth.register(body)
    _start_session(response, user.id)
    return user


@router.post("/login", response_model=UserRead)
def login(body: LoginRequest, response: Response, auth: AuthServiceDep):
    user = auth.authenticate(body)
    _start_session(response, user.id)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE, path="/", httponly=True, samesite="lax")


@router.get("/me", response_model=UserRead)
def me(user_id: CurrentUserId, users: UserServiceDep):
    """Usuario de la sesión actual (el frontend no puede leer la cookie)."""
    return users.get_user(user_id)
