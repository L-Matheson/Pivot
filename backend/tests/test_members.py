"""Workspace member management tests."""

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


def test_member_with_view_can_list(
    admin_user: User, workspace: Workspace, session: MagicMock
) -> None:
    role = _member_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.exec.return_value.all.return_value = []
    session.get.return_value = role

    client = _authed_client(admin_user, session)
    try:
        response = client.get(f"/api/workspaces/{workspace.id}/members")
        assert response.status_code == 200
    finally:
        _cleanup()


def test_member_without_manage_cannot_add(
    workspace: Workspace, session: MagicMock
) -> None:
    member_user = User(
        id=uuid.uuid4(),
        email="member@example.com",
        password_hash=hash_password("password"),
        display_name="Member",
        is_active=True,
    )
    role = _member_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=member_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.get.return_value = role

    client = _authed_client(member_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/members",
            json={"email": "new@example.com", "role_id": str(role.id)},
        )
        assert response.status_code == 403
    finally:
        _cleanup()


def test_custom_role_with_members_manage_can_add(
    admin_user: User, workspace: Workspace, session: MagicMock
) -> None:
    lead_role = Role(
        id=uuid.uuid4(),
        workspace_id=workspace.id,
        name="Team Lead",
        is_system=False,
        full_access=False,
        permissions={"members": {"view": True, "manage": True}},
    )
    target_role = _member_role()
    target_user = User(
        id=uuid.uuid4(),
        email="new@example.com",
        password_hash=hash_password("password"),
        display_name="New User",
        is_active=True,
    )

    call_count = 0

    def _first_side_effect():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return WorkspaceMembership(
                workspace_id=workspace.id,
                user_id=admin_user.id,
                role_id=lead_role.id,
            )
        if call_count == 2:
            return target_user
        return None

    session.exec.return_value.first.side_effect = _first_side_effect

    def _get_side_effect(model, id=None):
        if id == lead_role.id:
            return lead_role
        if id == target_role.id:
            return target_role
        return None

    session.get.side_effect = _get_side_effect

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/members",
            json={"email": "new@example.com", "role_id": str(target_role.id)},
        )
        assert response.status_code == 201
    finally:
        _cleanup()


def test_cannot_remove_workspace_owner(
    admin_user: User, workspace: Workspace, session: MagicMock
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.get.return_value = role

    second_admin = User(
        id=uuid.uuid4(),
        email="admin2@example.com",
        password_hash=hash_password("password"),
        display_name="Admin 2",
        is_active=True,
    )

    client = _authed_client(second_admin, session)
    try:
        def _get_side_effect(model, id=None):
            if id == workspace.id:
                return workspace
            return role

        session.get.side_effect = _get_side_effect

        response = client.delete(
            f"/api/workspaces/{workspace.id}/members/{admin_user.id}"
        )
        assert response.status_code == 422
        assert "owner" in response.json()["detail"].lower()
    finally:
        _cleanup()
