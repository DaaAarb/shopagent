"""Utilidades compartidas por los tests (no son fixtures: se importan)."""


def as_user(user) -> dict[str, str]:
    """Cabeceras de la autenticación simulada para actuar como `user`."""
    return {"X-User-Id": str(user.id)}
