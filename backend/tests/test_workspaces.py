"""Workspace CRUD tests."""

import uuid
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.core.db import get_session
from app.core.security import hash_password
from app.main import app
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


def _member_role() -> Role:
    return Role(
        id=uuid.uuid4(),
        workspace_id=None,
        name="member",
        is_system=True,
        full_access=False,
        permissions={
            "automations": {"view": ["*"], "edit": False, "execute": False, "manage": False},
            "connections": {"view": True, "manage": False},
            "members": {"view": True, "manage": False},
            "settings": {"view": False, "manage": False},
            "stats": {"view": True},
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
def member_user() -> User:
    return User(
        id=uuid.uuid4(),
        email="member@example.com",
        password_hash=hash_password("password"),
        display_name="Member",
        is_active=True,
    )


@pytest.fixture()
def workspace(admin_user: User) -> Workspace:
    return Workspace(
        id=uuid.uuid4(),
        name="Test Workspace",
        slug="test-workspace",
        owner_user_id=admin_user.id,
    )


def _authed_client(user: User, session_mock: MagicMock) -> TestClient:
    def _session_override():  # type: ignore[no-untyped-def]
        yield session_mock

    app.dependency_overrides[get_session] = _session_override
    app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(app)


def _cleanup() -> None:
    app.dependency_overrides.clear()


def test_create_workspace(admin_user: User, session: MagicMock) -> None:
    admin_role = _admin_role()

    call_count = 0

    def _first_side_effect():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return None
        return admin_role

    session.exec.return_value.first.side_effect = _first_side_effect
    session.get.return_value = admin_role

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            "/api/workspaces",
            json={"name": "My Team", "slug": "my-team"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Team"
        assert data["slug"] == "my-team"
        assert data["owner_user_id"] == str(admin_user.id)
    finally:
        _cleanup()


def test_create_workspace_duplicate_slug(admin_user: User, session: MagicMock) -> None:
    session.exec.return_value.first.return_value = Workspace(
        id=uuid.uuid4(), name="Existing", slug="taken", owner_user_id=admin_user.id
    )

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            "/api/workspaces",
            json={"name": "New", "slug": "taken"},
        )
        assert response.status_code == 409
    finally:
        _cleanup()


def test_non_member_cannot_access(
    workspace: Workspace, session: MagicMock
) -> None:
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


def test_member_can_read(
    member_user: User, workspace: Workspace, session: MagicMock
) -> None:
    role = _member_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=member_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership

    def _get_side_effect(model, id=None):
        if id == role.id:
            return role
        return workspace

    session.get.side_effect = _get_side_effect

    client = _authed_client(member_user, session)
    try:
        response = client.get(f"/api/workspaces/{workspace.id}")
        assert response.status_code == 200
    finally:
        _cleanup()


def test_member_cannot_update(
    member_user: User, workspace: Workspace, session: MagicMock
) -> None:
    role = _member_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=member_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.get.return_value = role

    client = _authed_client(member_user, session)
    try:
        response = client.patch(
            f"/api/workspaces/{workspace.id}",
            json={"name": "Hacked Name"},
        )
        assert response.status_code == 403
    finally:
        _cleanup()


def test_member_cannot_delete(
    member_user: User, workspace: Workspace, session: MagicMock
) -> None:
    role = _member_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=member_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.get.return_value = role

    client = _authed_client(member_user, session)
    try:
        response = client.delete(f"/api/workspaces/{workspace.id}")
        assert response.status_code == 403
    finally:
        _cleanup()


def test_admin_can_update(
    admin_user: User, workspace: Workspace, session: MagicMock
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership

    def _get_side_effect(model, id=None):
        if id == role.id:
            return role
        return workspace

    session.get.side_effect = _get_side_effect

    client = _authed_client(admin_user, session)
    try:
        response = client.patch(
            f"/api/workspaces/{workspace.id}",
            json={"name": "Updated Name"},
        )
        assert response.status_code == 200
    finally:
        _cleanup()


def test_admin_can_delete(
    admin_user: User, workspace: Workspace, session: MagicMock
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.exec.return_value.all.return_value = []
    session.get.return_value = role

    client = _authed_client(admin_user, session)
    try:
        response = client.delete(f"/api/workspaces/{workspace.id}")
        assert response.status_code == 204
    finally:
        _cleanup()


def test_custom_role_with_settings_manage_can_update(
    workspace: Workspace, session: MagicMock
) -> None:
    lead_user = User(
        id=uuid.uuid4(),
        email="lead@example.com",
        password_hash=hash_password("password"),
        display_name="Lead",
        is_active=True,
    )
    lead_role = Role(
        id=uuid.uuid4(),
        workspace_id=workspace.id,
        name="Team Lead",
        is_system=False,
        full_access=False,
        permissions={"settings": {"view": True, "manage": True}},
    )
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=lead_user.id, role_id=lead_role.id
    )
    session.exec.return_value.first.return_value = membership

    def _get_side_effect(model, id=None):
        if id == lead_role.id:
            return lead_role
        return workspace

    session.get.side_effect = _get_side_effect

    client = _authed_client(lead_user, session)
    try:
        response = client.patch(
            f"/api/workspaces/{workspace.id}",
            json={"name": "Updated By Lead"},
        )
        assert response.status_code == 200
    finally:
        _cleanup()
