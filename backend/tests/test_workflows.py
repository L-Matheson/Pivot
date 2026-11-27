"""Workflow CRUD tests."""

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
from app.models.workflow import Workflow
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


def _view_only_role() -> Role:
    return Role(
        id=uuid.uuid4(),
        workspace_id=None,
        name="member",
        is_system=True,
        full_access=False,
        permissions={
            "automations": {"view": ["*"], "edit": False, "execute": False, "manage": False},
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
def sample_workflow(workspace: Workspace, admin_user: User) -> Workflow:
    return Workflow(
        id=uuid.uuid4(),
        workspace_id=workspace.id,
        name="My Workflow",
        description="Test workflow",
        created_by=admin_user.id,
        definition={"schema_version": 1, "nodes": [], "edges": []},
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
    """Configure mocks so PermissionRequired finds a membership + role."""
    membership = WorkspaceMembership(
        workspace_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        role_id=role.id,
    )
    session.exec.return_value.first.return_value = membership
    session.get.return_value = role


# --- List ---


def test_list_workflows_empty(admin_user: User, session: MagicMock) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=uuid.uuid4(), user_id=admin_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.exec.return_value.all.return_value = []
    session.get.return_value = role

    client = _authed_client(admin_user, session)
    try:
        ws_id = uuid.uuid4()
        response = client.get(f"/api/workspaces/{ws_id}/workflows")
        assert response.status_code == 200
        assert response.json() == []
    finally:
        _cleanup()


def test_list_workflows_populated(
    admin_user: User, workspace: Workspace, sample_workflow: Workflow, session: MagicMock
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id
    )

    call_count = 0

    class _ExecResult:
        def first(self):
            return membership

        def all(self):
            return [sample_workflow]

    def _exec_side_effect(stmt):  # type: ignore[no-untyped-def]
        nonlocal call_count
        call_count += 1
        return _ExecResult()

    session.exec.side_effect = _exec_side_effect
    session.get.return_value = role

    client = _authed_client(admin_user, session)
    try:
        response = client.get(f"/api/workspaces/{workspace.id}/workflows")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "My Workflow"
    finally:
        _cleanup()


# --- Create ---


def test_create_workflow(admin_user: User, workspace: Workspace, session: MagicMock) -> None:
    role = _admin_role()
    _stub_membership(session, role)

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/workflows",
            json={"name": "New Workflow", "description": "A test"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Workflow"
        assert data["description"] == "A test"
        assert data["definition"]["schema_version"] == 1
        assert data["definition"]["nodes"] == []
        assert data["is_archived"] is False
    finally:
        _cleanup()


def test_create_workflow_name_required(
    admin_user: User, workspace: Workspace, session: MagicMock
) -> None:
    role = _admin_role()
    _stub_membership(session, role)

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/workflows",
            json={"name": ""},
        )
        assert response.status_code == 422
    finally:
        _cleanup()


# --- Get ---


def test_get_workflow(
    admin_user: User, workspace: Workspace, sample_workflow: Workflow, session: MagicMock
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.get.side_effect = lambda model, id: (
        role if model is Role else sample_workflow if id == sample_workflow.id else None
    )

    client = _authed_client(admin_user, session)
    try:
        response = client.get(
            f"/api/workspaces/{workspace.id}/workflows/{sample_workflow.id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "My Workflow"
        assert "definition" in data
    finally:
        _cleanup()


def test_get_workflow_not_found(
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
        response = client.get(f"/api/workspaces/{workspace.id}/workflows/{fake_id}")
        assert response.status_code == 404
    finally:
        _cleanup()


# --- Update ---


def test_update_workflow_name(
    admin_user: User, workspace: Workspace, sample_workflow: Workflow, session: MagicMock
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.get.side_effect = lambda model, id: (
        role if model is Role else sample_workflow if id == sample_workflow.id else None
    )

    client = _authed_client(admin_user, session)
    try:
        response = client.patch(
            f"/api/workspaces/{workspace.id}/workflows/{sample_workflow.id}",
            json={"name": "Renamed"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Renamed"
    finally:
        _cleanup()


def test_update_workflow_definition(
    admin_user: User, workspace: Workspace, sample_workflow: Workflow, session: MagicMock
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.get.side_effect = lambda model, id: (
        role if model is Role else sample_workflow if id == sample_workflow.id else None
    )

    definition = {
        "schema_version": 1,
        "nodes": [
            {"id": "t1", "type": "email_trigger", "position": {"x": 0, "y": 0}, "config": {}},
            {"id": "a1", "type": "send_email", "position": {"x": 200, "y": 0}, "config": {}},
        ],
        "edges": [{"id": "e1", "source": "t1", "target": "a1"}],
    }

    client = _authed_client(admin_user, session)
    try:
        response = client.patch(
            f"/api/workspaces/{workspace.id}/workflows/{sample_workflow.id}",
            json={"definition": definition},
        )
        assert response.status_code == 200
        assert len(response.json()["definition"]["nodes"]) == 2
    finally:
        _cleanup()


def test_update_workflow_cyclic_definition(
    admin_user: User, workspace: Workspace, sample_workflow: Workflow, session: MagicMock
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.get.side_effect = lambda model, id: (
        role if model is Role else sample_workflow if id == sample_workflow.id else None
    )

    definition = {
        "schema_version": 1,
        "nodes": [
            {"id": "a", "type": "action", "position": {"x": 0, "y": 0}},
            {"id": "b", "type": "action", "position": {"x": 100, "y": 0}},
        ],
        "edges": [
            {"id": "e1", "source": "a", "target": "b"},
            {"id": "e2", "source": "b", "target": "a"},
        ],
    }

    client = _authed_client(admin_user, session)
    try:
        response = client.patch(
            f"/api/workspaces/{workspace.id}/workflows/{sample_workflow.id}",
            json={"definition": definition},
        )
        assert response.status_code == 422
        assert "cycle" in str(response.json()).lower()
    finally:
        _cleanup()


# --- Duplicate ---


def test_duplicate_workflow(
    admin_user: User, workspace: Workspace, sample_workflow: Workflow, session: MagicMock
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.get.side_effect = lambda model, id: (
        role if model is Role else sample_workflow if id == sample_workflow.id else None
    )

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/workflows/{sample_workflow.id}/duplicate"
        )
        assert response.status_code == 201
        assert response.json()["name"] == "My Workflow (copy)"
    finally:
        _cleanup()


# --- Archive ---


def test_archive_workflow(
    admin_user: User, workspace: Workspace, sample_workflow: Workflow, session: MagicMock
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.get.side_effect = lambda model, id: (
        role if model is Role else sample_workflow if id == sample_workflow.id else None
    )

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/workflows/{sample_workflow.id}/archive"
        )
        assert response.status_code == 204
        assert sample_workflow.is_archived is True
    finally:
        _cleanup()


# --- Delete ---


def test_delete_workflow(
    admin_user: User, workspace: Workspace, sample_workflow: Workflow, session: MagicMock
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.get.side_effect = lambda model, id: (
        role if model is Role else sample_workflow if id == sample_workflow.id else None
    )

    client = _authed_client(admin_user, session)
    try:
        response = client.delete(
            f"/api/workspaces/{workspace.id}/workflows/{sample_workflow.id}"
        )
        assert response.status_code == 204
        session.delete.assert_called_once_with(sample_workflow)
    finally:
        _cleanup()


# --- Permission checks ---


def test_view_only_cannot_create(
    admin_user: User, workspace: Workspace, session: MagicMock
) -> None:
    role = _view_only_role()
    _stub_membership(session, role)

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/workflows",
            json={"name": "Should Fail"},
        )
        assert response.status_code == 403
    finally:
        _cleanup()


def test_view_only_can_list(
    admin_user: User, workspace: Workspace, session: MagicMock
) -> None:
    role = _view_only_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id
    )
    session.exec.return_value.first.return_value = membership
    session.exec.return_value.all.return_value = []
    session.get.return_value = role

    client = _authed_client(admin_user, session)
    try:
        response = client.get(f"/api/workspaces/{workspace.id}/workflows")
        assert response.status_code == 200
    finally:
        _cleanup()
