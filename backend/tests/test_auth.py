"""Authentication endpoint tests."""

import uuid
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, hash_password
from app.models.user import User


def _make_user(*, email: str = "test@example.com", password: str = "password123") -> User:
    return User(
        id=uuid.uuid4(),
        email=email,
        password_hash=hash_password(password),
        display_name="Test User",
        is_active=True,
    )


# --- register ---


def test_register_success(client: TestClient, session: MagicMock) -> None:
    session.exec.return_value.first.return_value = None

    response = client.post(
        "/api/auth/register",
        json={"email": "new@example.com", "password": "securepass", "display_name": "New User"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["display_name"] == "New User"
    assert "password_hash" not in data


def test_register_duplicate_email(client: TestClient, session: MagicMock) -> None:
    session.exec.return_value.first.return_value = _make_user()

    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "securepass", "display_name": "Dup"},
    )
    assert response.status_code == 409


def test_register_short_password(client: TestClient) -> None:
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "short", "display_name": "Test"},
    )
    assert response.status_code == 422


# --- login ---


@patch("app.api.auth.routes.store_refresh_token")
def test_login_success(
    mock_store: MagicMock, client: TestClient, session: MagicMock,
) -> None:
    user = _make_user(password="correctpassword")
    session.exec.return_value.first.return_value = user

    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "correctpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "expires_in" in data
    assert data["token_type"] == "bearer"
    assert "refresh_token" not in data

    assert "pivot_refresh" in response.cookies
    mock_store.assert_called_once()


def test_login_wrong_password(client: TestClient, session: MagicMock) -> None:
    user = _make_user(password="correctpassword")
    session.exec.return_value.first.return_value = user

    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "incorrect email or password" in response.json()["detail"].lower()


def test_login_unknown_email(client: TestClient, session: MagicMock) -> None:
    session.exec.return_value.first.return_value = None

    response = client.post(
        "/api/auth/login",
        json={"email": "unknown@example.com", "password": "anypassword"},
    )
    assert response.status_code == 401


# --- refresh ---


@patch("app.api.auth.routes.store_refresh_token")
@patch("app.api.auth.routes.revoke_refresh_token")
@patch("app.api.auth.routes.is_refresh_token_valid", return_value=True)
def test_refresh_success(
    mock_valid: MagicMock,
    mock_revoke: MagicMock,
    mock_store: MagicMock,
    client: TestClient,
    session: MagicMock,
) -> None:
    user = _make_user()
    refresh, jti = create_refresh_token(str(user.id))
    session.get.return_value = user

    client.cookies.set("pivot_refresh", refresh, path="/api/auth")
    response = client.post("/api/auth/refresh")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "expires_in" in data
    assert "pivot_refresh" in response.cookies
    mock_revoke.assert_called_once_with(jti)
    mock_store.assert_called_once()


def test_refresh_with_access_token_rejected(client: TestClient, session: MagicMock) -> None:
    user = _make_user()
    access = create_access_token(str(user.id))

    client.cookies.set("pivot_refresh", access, path="/api/auth")
    response = client.post("/api/auth/refresh")
    assert response.status_code == 401


def test_refresh_missing_cookie(client: TestClient) -> None:
    response = client.post("/api/auth/refresh")
    assert response.status_code == 401


@patch("app.api.auth.routes.is_refresh_token_valid", return_value=False)
def test_refresh_revoked_token(
    mock_valid: MagicMock, client: TestClient, session: MagicMock,
) -> None:
    user = _make_user()
    refresh, _jti = create_refresh_token(str(user.id))

    client.cookies.set("pivot_refresh", refresh, path="/api/auth")
    response = client.post("/api/auth/refresh")
    assert response.status_code == 401
    assert "revoked" in response.json()["detail"].lower()


# --- logout ---


def test_logout(client: TestClient) -> None:
    response = client.post("/api/auth/logout")
    assert response.status_code == 204


# --- me ---


def test_me_authenticated(client: TestClient, session: MagicMock) -> None:
    user = _make_user()
    token = create_access_token(str(user.id))
    session.get.return_value = user

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == user.email


def test_me_no_token(client: TestClient) -> None:
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_expired_token(client: TestClient) -> None:
    with patch("app.core.security.settings") as mock_settings:
        mock_settings.jwt_algorithm = settings.jwt_algorithm
        mock_settings.jwt_signing_key = settings.jwt_signing_key
        mock_settings.jwt_verifying_key = settings.jwt_verifying_key
        mock_settings.jwt_issuer = "pivot"
        mock_settings.jwt_audience = "pivot"
        mock_settings.access_token_expire_minutes = -1
        token = create_access_token(str(uuid.uuid4()))

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
