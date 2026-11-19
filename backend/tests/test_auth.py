"""Registro, login, logout y protección de las rutas con la cookie de sesión."""

from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.api.deps import SESSION_COOKIE
from app.security import create_session_token, hash_password, verify_password
from tests.conftest import TEST_PASSWORD
from tests.helpers import as_user

NEW_USER = {"name": "Carol", "email": "carol@example.com", "password": "una-clave-larga"}


def login(client, email, password):
    return client.post("/auth/login", json={"email": email, "password": password})


# --- Registro ---------------------------------------------------------------------------


def test_register_creates_account_and_starts_session(client):
    response = client.post("/auth/register", json=NEW_USER)

    assert response.status_code == 201
    assert response.json()["email"] == "carol@example.com"
    # El TestClient guarda la cookie como un navegador: la siguiente petición va autenticada.
    assert client.get("/auth/me").json()["name"] == "Carol"


def test_register_normalizes_email_to_lowercase(client):
    client.post("/auth/register", json={**NEW_USER, "email": "  Carol@Example.COM "})

    assert login(client, "carol@example.com", NEW_USER["password"]).status_code == 200


def test_register_rejects_duplicate_email(client, alice):
    response = client.post("/auth/register", json={**NEW_USER, "email": "ALICE@example.com"})

    assert response.status_code == 409


@pytest.mark.parametrize(
    "override",
    [{"password": "corta"}, {"email": "no-es-un-email"}, {"name": "  "}],
)
def test_register_validates_input(client, override):
    assert client.post("/auth/register", json={**NEW_USER, **override}).status_code == 422


def test_password_is_never_returned_nor_stored_in_plain_text(client, session):
    from app.models import User

    response = client.post("/auth/register", json=NEW_USER)

    assert "password" not in response.text
    stored = session.get(User, response.json()["id"]).password_hash
    assert NEW_USER["password"] not in stored
    assert stored.startswith("$argon2id$")


# --- Login y cookie ---------------------------------------------------------------------


def test_login_sets_httponly_session_cookie(client, alice):
    response = login(client, alice.email, TEST_PASSWORD)

    assert response.status_code == 200
    assert response.json() == {"id": alice.id, "name": "Alice", "email": "alice@example.com"}
    cookie = response.headers["set-cookie"].lower()
    assert cookie.startswith(f"{SESSION_COOKIE}=")
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    # El token NO va en el cuerpo: el JavaScript del frontend no llega a verlo.
    assert "token" not in response.text


def test_wrong_password_and_unknown_email_give_the_same_error(client, alice):
    wrong_password = login(client, alice.email, "no-es-esta")
    unknown_email = login(client, "nadie@example.com", "da-igual")

    assert wrong_password.status_code == unknown_email.status_code == 401
    # Mismo mensaje: no se puede averiguar si un email está registrado.
    assert wrong_password.json() == unknown_email.json()


def test_logout_clears_the_session(client, alice):
    login(client, alice.email, TEST_PASSWORD)

    assert client.post("/auth/logout").status_code == 204
    assert client.get("/auth/me").status_code == 401


# --- Rutas protegidas -------------------------------------------------------------------


def test_protected_route_without_session_is_401(client):
    response = client.get("/orders")

    assert response.status_code == 401
    assert response.json() == {"detail": "No has iniciado sesión o la sesión ha caducado."}


def test_old_x_user_id_header_is_ignored(client, alice):
    """La autenticación simulada ya no existe: decir quién eres no basta."""
    assert client.get("/orders", headers={"X-User-Id": str(alice.id)}).status_code == 401


def test_tampered_token_is_rejected(client, alice, bob):
    """Cambiar el usuario dentro del token invalida la firma."""
    payload = jwt.decode(create_session_token(alice.id), options={"verify_signature": False})
    forged = jwt.encode({**payload, "sub": str(bob.id)}, "otra-clave", algorithm="HS256")

    response = client.get("/orders", headers={"Cookie": f"{SESSION_COOKIE}={forged}"})

    assert response.status_code == 401


def test_unsigned_token_is_rejected(client, alice):
    """Ataque clásico: un token con algoritmo "none" (sin firma)."""
    forged = jwt.encode({"sub": str(alice.id), "exp": 9999999999}, None, algorithm="none")

    assert client.get("/orders", headers={"Cookie": f"{SESSION_COOKIE}={forged}"}).status_code == 401


def test_expired_token_is_rejected(client, alice):
    from app.config import get_settings

    past = datetime.now(UTC) - timedelta(minutes=1)
    expired = jwt.encode(
        {"sub": str(alice.id), "exp": past}, get_settings().secret_key, algorithm="HS256"
    )

    assert client.get("/orders", headers={"Cookie": f"{SESSION_COOKIE}={expired}"}).status_code == 401


def test_token_of_deleted_user_is_rejected(client, alice, session):
    headers = as_user(alice)
    session.delete(alice)
    session.commit()

    assert client.get("/orders", headers=headers).status_code == 401


# --- Primitivas ------------------------------------------------------------------------


def test_password_hashing_round_trip():
    hashed = hash_password("loba1234")

    assert verify_password("loba1234", hashed)
    assert not verify_password("loba12345", hashed)
    assert not verify_password("loba1234", None)
    assert not verify_password("loba1234", "")  # usuarios migrados sin contraseña
