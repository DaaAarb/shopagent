"""Traducción de errores del dominio a HTTP, en un único sitio.

Las rutas no tienen try/except: dejan que la excepción suba y este
manejador global la convierte en la respuesta adecuada.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.services import (
    InvalidInput,
    InvalidOrderState,
    OrderNotFound,
    ShopError,
    UserNotFound,
)

class NotAuthenticated(Exception):
    """La petición no trae cabecera X-User-Id: no sabemos quién llama (→ 401).

    Es un error de la capa HTTP, no del dominio: por eso no hereda de ShopError.
    """


STATUS_BY_ERROR: dict[type[ShopError], int] = {
    UserNotFound: status.HTTP_401_UNAUTHORIZED,
    OrderNotFound: status.HTTP_404_NOT_FOUND,
    InvalidOrderState: status.HTTP_409_CONFLICT,
    InvalidInput: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


async def _handle_shop_error(_request: Request, exc: Exception) -> JSONResponse:
    status_code = next(
        (code for error, code in STATUS_BY_ERROR.items() if isinstance(exc, error)),
        status.HTTP_400_BAD_REQUEST,
    )
    detail = "Usuario no identificado." if isinstance(exc, UserNotFound) else str(exc)
    return JSONResponse(status_code=status_code, content={"detail": detail})


async def _handle_not_authenticated(_request: Request, _exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Falta la cabecera X-User-Id."},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ShopError, _handle_shop_error)
    app.add_exception_handler(NotAuthenticated, _handle_not_authenticated)
