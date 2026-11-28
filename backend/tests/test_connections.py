"""Connection CRUD and OAuth2 flow tests."""

import uuid
from unittest.mock import MagicMock, patch

import cryptography.fernet
import pytest
from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.core.db import get_session
from app.core.encryption import decrypt_credentials, encrypt_credentials
from app.core.security import hash_password
from app.main import app
from app.models.connection import Connection
from app.models.role import Role
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMembership


def _admin_role() -> Role:
    return Role(
        id=uuid.uuid4(),
        workspace_id=None,
        name="admin",
        is_system=True,
        full_access=True,
        permissions={},
    )


def _viewer_role() -> Role:
    return Role(
        id=uuid.uuid4(),
        workspace_id=None,
        name="member",
        is_system=True,
        full_access=False,
        permissions={
            "connections": {"view": True, "manage": False},
        },
    )


@pytest.fixture()
def admin_user() -> User:
    return User(
        id=uuid.uuid4(),
        email="admin@example.com",
        password_hash=hash_password("password"),
        display_name="Admin",
        is_active=True,
    )


@pytest.fixture()
def workspace(admin_user: User) -> Workspace:
    return Workspace(
        id=uuid.uuid4(),
        name="Test Workspace",
        slug="test-ws",
        owner_user_id=admin_user.id,
    )


@pytest.fixture()
def sample_connection(workspace: Workspace, admin_user: User) -> Connection:
    return Connection(
        id=uuid.uuid4(),
        workspace_id=workspace.id,
        provider="google",
        name="Google (admin@example.com)",
        auth_type="oauth2",
        credentials_encrypted=encrypt_credentials(
            {"access_token": "tok_123", "refresh_token": "ref_456"},
            "test-encryption-key",
        ),
        scopes="openid email",
        status="connected",
        connected_by_user_id=admin_user.id,
    )


def _authed_client(user: User, session_mock: MagicMock) -> TestClient:
    def _session_override():  # type: ignore[no-untyped-def]
        yield session_mock

    app.dependency_overrides[get_session] = _session_override
    app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(app)


def _cleanup() -> None:
    app.dependency_overrides.clear()


def _stub_membership(session: MagicMock, role: Role) -> None:
    membership = WorkspaceMembership(
        workspace_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        role_id=role.id,
    )
    session.exec.return_value.first.return_value = membership
    session.get.return_value = role


# --- Encryption unit tests ---


def test_encrypt_decrypt_roundtrip() -> None:
    key = "my-secret-key-for-testing"
    data = {"access_token": "abc123", "refresh_token": "def456"}
    encrypted = encrypt_credentials(data, key)
    assert isinstance(encrypted, bytes)
    assert encrypted != b'{"access_token": "abc123", "refresh_token": "def456"}'
    decrypted = decrypt_credentials(encrypted, key)
    assert decrypted == data


def test_decrypt_with_wrong_key_fails() -> None:
    key = "correct-key"
    data = {"token": "secret"}
    encrypted = encrypt_credentials(data, key)
    with pytest.raises(cryptography.fernet.InvalidToken):
        decrypt_credentials(encrypted, "wrong-key")


# --- Connector registry ---


def test_list_connectors_endpoint(admin_user: User, session: MagicMock) -> None:
    client = _authed_client(admin_user, session)
    try:
        response = client.get("/api/connectors")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        slugs = [c["slug"] for c in data]
        assert "google_gmail" in slugs
        assert "google_sheets" in slugs
        gmail = next(c for c in data if c["slug"] == "google_gmail")
        assert gmail["auth_type"] == "oauth2"
        assert "email_trigger" in gmail["triggers"]
        sheets = next(c for c in data if c["slug"] == "google_sheets")
        assert "write_spreadsheet" in sheets["actions"]
    finally:
        _cleanup()


# --- Connection CRUD ---


def test_list_connections_empty(admin_user: User, workspace: Workspace, session: MagicMock) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.exec.return_value.all.return_value = []
    session.get.return_value = role

    client = _authed_client(admin_user, session)
    try:
        response = client.get(f"/api/workspaces/{workspace.id}/connections")
        assert response.status_code == 200
        assert response.json() == []
    finally:
        _cleanup()


@patch("app.api.connections.utils.settings")
def test_create_connection_api_key(
    mock_settings: MagicMock,
    admin_user: User,
    workspace: Workspace,
    session: MagicMock,
) -> None:
    mock_settings.encryption_key = "test-key"
    mock_settings.cors_origins = ["http://localhost:5173"]
    role = _admin_role()
    _stub_membership(session, role)

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/connections",
            json={
                "provider": "custom_api",
                "name": "My API",
                "auth_type": "api_key",
                "credentials": {"api_key": "sk-12345"},
                "scopes": "",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["provider"] == "custom_api"
        assert data["auth_type"] == "api_key"
        assert data["status"] == "connected"
        assert "credentials" not in data
        assert "credentials_encrypted" not in data
    finally:
        _cleanup()


def test_get_connection(
    admin_user: User,
    workspace: Workspace,
    sample_connection: Connection,
    session: MagicMock,
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.get.side_effect = lambda model, id: (
        role if model is Role else sample_connection if id == sample_connection.id else None
    )

    client = _authed_client(admin_user, session)
    try:
        response = client.get(f"/api/workspaces/{workspace.id}/connections/{sample_connection.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "google"
        assert "credentials" not in data
        assert "credentials_encrypted" not in data
    finally:
        _cleanup()


def test_get_connection_not_found(
    admin_user: User, workspace: Workspace, session: MagicMock
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.get.side_effect = lambda model, id: role if model is Role else None

    client = _authed_client(admin_user, session)
    try:
        fake_id = uuid.uuid4()
        response = client.get(f"/api/workspaces/{workspace.id}/connections/{fake_id}")
        assert response.status_code == 404
    finally:
        _cleanup()


def test_delete_connection(
    admin_user: User,
    workspace: Workspace,
    sample_connection: Connection,
    session: MagicMock,
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.get.side_effect = lambda model, id: (
        role if model is Role else sample_connection if id == sample_connection.id else None
    )

    client = _authed_client(admin_user, session)
    try:
        response = client.delete(
            f"/api/workspaces/{workspace.id}/connections/{sample_connection.id}"
        )
        assert response.status_code == 204
        session.delete.assert_called_once_with(sample_connection)
    finally:
        _cleanup()


# --- Permission checks ---


def test_viewer_cannot_create_connection(
    admin_user: User, workspace: Workspace, session: MagicMock
) -> None:
    role = _viewer_role()
    _stub_membership(session, role)

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/connections",
            json={
                "provider": "google",
                "name": "Google",
                "auth_type": "oauth2",
            },
        )
        assert response.status_code == 403
    finally:
        _cleanup()


def test_viewer_can_list_connections(
    admin_user: User, workspace: Workspace, session: MagicMock
) -> None:
    role = _viewer_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.exec.return_value.all.return_value = []
    session.get.return_value = role

    client = _authed_client(admin_user, session)
    try:
        response = client.get(f"/api/workspaces/{workspace.id}/connections")
        assert response.status_code == 200
    finally:
        _cleanup()


# --- OAuth2 flow ---


@patch("app.connectors.providers.google_gmail.settings")
def test_oauth_authorize_returns_url(
    mock_settings: MagicMock,
    admin_user: User,
    workspace: Workspace,
    session: MagicMock,
) -> None:
    mock_settings.google_client_id = "test-client-id"
    mock_settings.google_client_secret = "test-client-secret"
    role = _admin_role()
    _stub_membership(session, role)

    client = _authed_client(admin_user, session)
    try:
        response = client.get(
            f"/api/workspaces/{workspace.id}/connections/oauth/google_gmail/authorize"
        )
        assert response.status_code == 200
        data = response.json()
        assert "authorize_url" in data
        assert "accounts.google.com" in data["authorize_url"]
        assert "state" in data
        assert data["state"]
    finally:
        _cleanup()


def test_oauth_authorize_unknown_provider(
    admin_user: User, workspace: Workspace, session: MagicMock
) -> None:
    role = _admin_role()
    _stub_membership(session, role)

    client = _authed_client(admin_user, session)
    try:
        response = client.get(
            f"/api/workspaces/{workspace.id}/connections/oauth/nonexistent/authorize"
        )
        assert response.status_code == 400
    finally:
        _cleanup()


@patch("app.api.connections.oauth.exchange_code_for_tokens")
@patch("app.api.connections.oauth._pending_oauth_states")
@patch("app.api.connections.utils.settings")
@patch("app.connectors.providers.google_gmail.settings")
def test_oauth_callback_creates_connection(
    mock_gmail_settings: MagicMock,
    mock_settings: MagicMock,
    mock_states: MagicMock,
    mock_exchange: MagicMock,
    admin_user: User,
    workspace: Workspace,
    session: MagicMock,
) -> None:
    mock_settings.encryption_key = "test-key"
    mock_settings.cors_origins = ["http://localhost:5173"]
    mock_gmail_settings.google_client_id = "test-client-id"
    mock_gmail_settings.google_client_secret = "test-client-secret"

    state = "test-state-value"
    mock_states.pop.return_value = {
        "provider": "google_gmail",
        "workspace_id": str(workspace.id),
        "user_id": str(admin_user.id),
    }

    mock_exchange.return_value = {
        "access_token": "ya29.mock_token",
        "refresh_token": "1//mock_refresh",
        "expires_in": 3600,
        "token_type": "Bearer",
    }

    role = _admin_role()
    _stub_membership(session, role)

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/connections/oauth/google_gmail/callback",
            json={"code": "4/mock_auth_code", "state": state},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["provider"] == "google_gmail"
        assert data["auth_type"] == "oauth2"
        assert data["status"] == "connected"
        assert "credentials" not in data
    finally:
        _cleanup()


def test_oauth_callback_invalid_state(
    admin_user: User, workspace: Workspace, session: MagicMock
) -> None:
    role = _admin_role()
    _stub_membership(session, role)

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/connections/oauth/google_gmail/callback",
            json={"code": "4/mock_auth_code", "state": "invalid-state"},
        )
        assert response.status_code == 400
        assert "state" in response.json()["detail"].lower()
    finally:
        _cleanup()


# --- Test connection ---


@patch("app.api.connections.utils.settings")
def test_test_connection_oauth(
    mock_settings: MagicMock,
    admin_user: User,
    workspace: Workspace,
    sample_connection: Connection,
    session: MagicMock,
) -> None:
    mock_settings.encryption_key = "test-encryption-key"
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.get.side_effect = lambda model, id: (
        role if model is Role else sample_connection if id == sample_connection.id else None
    )

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/connections/{sample_connection.id}/test"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
    finally:
        _cleanup()
