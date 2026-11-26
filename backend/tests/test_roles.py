"""Role CRUD and permission tests."""

import uuid
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.core.db import get_session
from app.core.permissions import check_permission
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


def _custom_role(workspace_id: uuid.UUID) -> Role:
    return Role(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        name="Finance Team",
        is_system=False,
        full_access=False,
        permissions={
            "automations": {
                "view": ["folder:finance"],
                "edit": ["folder:finance"],
                "execute": ["folder:finance"],
                "manage": False,
            },
            "connections": {"view": True, "manage": False},
            "roles": {"view": True, "manage": True},
        },
    )


def _make_user(email: str = "admin@example.com") -> User:
    return User(
        id=uuid.uuid4(),
        email=email,
        password_hash=hash_password("password"),
        display_name="Admin",
        is_active=True,
    )


# -- Permission utility tests --


def test_full_access_bypasses_all_checks() -> None:
    role = _admin_role()
    assert check_permission(role, "automations", "manage") is True
    assert check_permission(role, "settings", "manage") is True
    assert check_permission(role, "anything", "anything") is True


def test_full_access_is_on_role_not_name() -> None:
    fake_admin = Role(
        id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        name="admin",
        is_system=False,
        full_access=False,
        permissions={},
    )
    assert check_permission(fake_admin, "settings", "manage") is False


def test_member_view_automations() -> None:
    role = _member_role()
    assert check_permission(role, "automations", "view") is True
    assert check_permission(role, "automations", "edit") is False
    assert check_permission(role, "automations", "execute") is False


def test_member_view_stats() -> None:
    role = _member_role()
    assert check_permission(role, "stats", "view") is True
    assert check_permission(role, "settings", "view") is False


def test_custom_role_scoped_access() -> None:
    role = _custom_role(uuid.uuid4())
    assert check_permission(role, "automations", "view", "folder:finance") is True
    assert check_permission(role, "automations", "edit", "folder:finance") is True
    assert check_permission(role, "automations", "view", "folder:hr") is False
    assert check_permission(role, "automations", "manage") is False


def test_custom_role_can_manage_roles() -> None:
    role = _custom_role(uuid.uuid4())
    assert check_permission(role, "roles", "view") is True
    assert check_permission(role, "roles", "manage") is True


def test_missing_resource_denied() -> None:
    role = _member_role()
    assert check_permission(role, "nonexistent", "view") is False


# -- Role API tests --


@pytest.fixture()
def admin_user() -> User:
    return _make_user("admin@example.com")


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


def test_create_custom_role(
    admin_user: User, workspace: Workspace, session: MagicMock
) -> None:
    admin_role = _admin_role()
    call_count = 0

    def _first_side_effect():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return WorkspaceMembership(
                workspace_id=workspace.id,
                user_id=admin_user.id,
                role_id=admin_role.id,
            )
        return None

    session.exec.return_value.first.side_effect = _first_side_effect
    session.get.return_value = admin_role

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/roles",
            json={
                "name": "Finance Team",
                "permissions": {"automations": {"view": ["folder:finance"]}},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Finance Team"
        assert data["is_system"] is False
        assert data["full_access"] is False
        assert data["workspace_id"] == str(workspace.id)
    finally:
        _cleanup()


def test_cannot_modify_system_role(
    admin_user: User, workspace: Workspace, session: MagicMock
) -> None:
    admin_role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id,
        user_id=admin_user.id,
        role_id=admin_role.id,
    )
    session.exec.return_value.first.return_value = membership
    session.get.return_value = admin_role

    client = _authed_client(admin_user, session)
    try:
        response = client.patch(
            f"/api/workspaces/{workspace.id}/roles/{admin_role.id}",
            json={"name": "Super Admin"},
        )
        assert response.status_code == 422
    finally:
        _cleanup()


def test_cannot_delete_system_role(
    admin_user: User, workspace: Workspace, session: MagicMock
) -> None:
    admin_role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id,
        user_id=admin_user.id,
        role_id=admin_role.id,
    )
    session.exec.return_value.first.return_value = membership
    session.get.return_value = admin_role

    client = _authed_client(admin_user, session)
    try:
        response = client.delete(
            f"/api/workspaces/{workspace.id}/roles/{admin_role.id}",
        )
        assert response.status_code == 422
    finally:
        _cleanup()


def test_non_admin_cannot_create_role(
    workspace: Workspace, session: MagicMock
) -> None:
    member_user = _make_user("member@example.com")
    member_role = _member_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id,
        user_id=member_user.id,
        role_id=member_role.id,
    )
    session.exec.return_value.first.return_value = membership
    session.get.return_value = member_role

    client = _authed_client(member_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/roles",
            json={"name": "Nope", "permissions": {}},
        )
        assert response.status_code == 403
    finally:
        _cleanup()


def test_custom_role_with_roles_manage_can_create(
    workspace: Workspace, session: MagicMock
) -> None:
    lead_user = _make_user("lead@example.com")
    lead_role = Role(
        id=uuid.uuid4(),
        workspace_id=workspace.id,
        name="Team Lead",
        is_system=False,
        full_access=False,
        permissions={"roles": {"view": True, "manage": True}},
    )
    call_count = 0

    def _first_side_effect():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return WorkspaceMembership(
                workspace_id=workspace.id,
                user_id=lead_user.id,
                role_id=lead_role.id,
            )
        return None

    session.exec.return_value.first.side_effect = _first_side_effect
    session.get.return_value = lead_role

    client = _authed_client(lead_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/roles",
            json={
                "name": "New Custom Role",
                "permissions": {"stats": {"view": True}},
            },
        )
        assert response.status_code == 201
    finally:
        _cleanup()
