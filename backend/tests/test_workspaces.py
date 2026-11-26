"""Workspace endpoint and permission boundary tests."""

import uuid
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.core.db import get_session
from app.core.security import hash_password
from app.main import app
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMembership, WorkspaceRole


@pytest.fixture()
def owner_user() -> User:
    return User(
        id=uuid.uuid4(),
        email="owner@example.com",
        password_hash=hash_password("password"),
        display_name="Owner",
        is_active=True,
    )


@pytest.fixture()
def editor_user() -> User:
    return User(
        id=uuid.uuid4(),
        email="editor@example.com",
        password_hash=hash_password("password"),
        display_name="Editor",
        is_active=True,
    )


@pytest.fixture()
def viewer_user() -> User:
    return User(
        id=uuid.uuid4(),
        email="viewer@example.com",
        password_hash=hash_password("password"),
        display_name="Viewer",
        is_active=True,
    )


@pytest.fixture()
def workspace(owner_user: User) -> Workspace:
    return Workspace(
        id=uuid.uuid4(),
        name="Test Workspace",
        slug="test-workspace",
        owner_user_id=owner_user.id,
    )


def _authed_client(user: User, session_mock: MagicMock) -> TestClient:
    def _session_override():  # type: ignore[no-untyped-def]
        yield session_mock

    app.dependency_overrides[get_session] = _session_override
    app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(app)


def _cleanup() -> None:
    app.dependency_overrides.clear()


def test_create_workspace(owner_user: User, session: MagicMock) -> None:
    session.exec.return_value.first.return_value = None

    client = _authed_client(owner_user, session)
    try:
        response = client.post(
            "/api/workspaces",
            json={"name": "My Team", "slug": "my-team"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Team"
        assert data["slug"] == "my-team"
        assert data["owner_user_id"] == str(owner_user.id)
    finally:
        _cleanup()


def test_create_workspace_duplicate_slug(owner_user: User, session: MagicMock) -> None:
    session.exec.return_value.first.return_value = Workspace(
        id=uuid.uuid4(), name="Existing", slug="taken", owner_user_id=owner_user.id
    )

    client = _authed_client(owner_user, session)
    try:
        response = client.post(
            "/api/workspaces",
            json={"name": "New", "slug": "taken"},
        )
        assert response.status_code == 409
    finally:
        _cleanup()


def test_non_member_cannot_access(
    owner_user: User, workspace: Workspace, session: MagicMock
) -> None:
    """Non-members get 404 to avoid leaking workspace existence."""
    session.exec.return_value.first.return_value = None

    outsider = User(
        id=uuid.uuid4(),
        email="outsider@example.com",
        password_hash=hash_password("password"),
        display_name="Outsider",
        is_active=True,
    )
    client = _authed_client(outsider, session)
    try:
        response = client.get(f"/api/workspaces/{workspace.id}")
        assert response.status_code == 404
    finally:
        _cleanup()


def test_viewer_can_read(viewer_user: User, workspace: Workspace, session: MagicMock) -> None:
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=viewer_user.id, role=WorkspaceRole.viewer
    )
    session.exec.return_value.first.return_value = membership
    session.get.return_value = workspace

    client = _authed_client(viewer_user, session)
    try:
        response = client.get(f"/api/workspaces/{workspace.id}")
        assert response.status_code == 200
    finally:
        _cleanup()


def test_viewer_cannot_update(viewer_user: User, workspace: Workspace, session: MagicMock) -> None:
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=viewer_user.id, role=WorkspaceRole.viewer
    )
    session.exec.return_value.first.return_value = membership

    client = _authed_client(viewer_user, session)
    try:
        response = client.patch(
            f"/api/workspaces/{workspace.id}",
            json={"name": "Hacked Name"},
        )
        assert response.status_code == 403
    finally:
        _cleanup()


def test_viewer_cannot_delete(viewer_user: User, workspace: Workspace, session: MagicMock) -> None:
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=viewer_user.id, role=WorkspaceRole.viewer
    )
    session.exec.return_value.first.return_value = membership

    client = _authed_client(viewer_user, session)
    try:
        response = client.delete(f"/api/workspaces/{workspace.id}")
        assert response.status_code == 403
    finally:
        _cleanup()


def test_editor_cannot_delete(editor_user: User, workspace: Workspace, session: MagicMock) -> None:
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=editor_user.id, role=WorkspaceRole.editor
    )
    session.exec.return_value.first.return_value = membership

    client = _authed_client(editor_user, session)
    try:
        response = client.delete(f"/api/workspaces/{workspace.id}")
        assert response.status_code == 403
    finally:
        _cleanup()


def test_editor_cannot_update(editor_user: User, workspace: Workspace, session: MagicMock) -> None:
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=editor_user.id, role=WorkspaceRole.editor
    )
    session.exec.return_value.first.return_value = membership

    client = _authed_client(editor_user, session)
    try:
        response = client.patch(
            f"/api/workspaces/{workspace.id}",
            json={"name": "Nope"},
        )
        assert response.status_code == 403
    finally:
        _cleanup()
