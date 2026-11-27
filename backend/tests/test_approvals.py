"""Approval request CRUD tests."""

import uuid
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.core.db import get_session
from app.core.security import hash_password
from app.main import app
from app.models.approval import ApprovalRequest
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


def _reviewer_role(workspace_id: uuid.UUID) -> Role:
    return Role(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        name="reviewer",
        is_system=False,
        full_access=False,
        permissions={
            "automations": {"view": ["*"], "edit": ["*"], "execute": False, "manage": False},
        },
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
def workflow(workspace: Workspace, admin_user: User) -> Workflow:
    return Workflow(
        id=uuid.uuid4(),
        workspace_id=workspace.id,
        name="Approval Workflow",
        created_by=admin_user.id,
        definition={"schema_version": 1, "nodes": [], "edges": []},
    )


@pytest.fixture()
def sample_approval(
    workspace: Workspace, workflow: Workflow,
) -> ApprovalRequest:
    role_id = uuid.uuid4()
    return ApprovalRequest(
        id=uuid.uuid4(),
        workspace_id=workspace.id,
        workflow_id=workflow.id,
        node_id="approval-123",
        required_role_id=role_id,
        status="pending",
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


# --- List ---


def test_list_approvals_empty(admin_user: User, session: MagicMock) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=uuid.uuid4(), user_id=admin_user.id, role_id=role.id,
    )
    session.exec.return_value.first.return_value = membership
    session.exec.return_value.all.return_value = []
    session.get.return_value = role

    client = _authed_client(admin_user, session)
    try:
        ws_id = uuid.uuid4()
        response = client.get(f"/api/workspaces/{ws_id}/approvals")
        assert response.status_code == 200
        assert response.json() == []
    finally:
        _cleanup()


def test_list_approvals_populated(
    admin_user: User,
    workspace: Workspace,
    sample_approval: ApprovalRequest,
    session: MagicMock,
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id,
    )

    class _ExecResult:
        def first(self):
            return membership

        def all(self):
            return [sample_approval]

    session.exec.side_effect = lambda stmt: _ExecResult()
    session.get.return_value = role

    client = _authed_client(admin_user, session)
    try:
        response = client.get(f"/api/workspaces/{workspace.id}/approvals")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["node_id"] == "approval-123"
        assert data[0]["status"] == "pending"
    finally:
        _cleanup()


# --- Create ---


def test_create_approval(
    admin_user: User,
    workspace: Workspace,
    workflow: Workflow,
    session: MagicMock,
) -> None:
    role = _admin_role()
    reviewer = _reviewer_role(workspace.id)
    _stub_membership(session, role)

    original_get = session.get.return_value

    def _get_side_effect(model, id):
        if model is Role:
            if id == reviewer.id:
                return reviewer
            return original_get
        return None

    session.get.side_effect = _get_side_effect

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/approvals",
            json={
                "workflow_id": str(workflow.id),
                "node_id": "approval-node-1",
                "required_role_id": str(reviewer.id),
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["node_id"] == "approval-node-1"
        assert data["status"] == "pending"
        assert data["required_role_id"] == str(reviewer.id)
    finally:
        _cleanup()


# --- Get ---


def test_get_approval(
    admin_user: User,
    workspace: Workspace,
    sample_approval: ApprovalRequest,
    session: MagicMock,
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id,
    )
    session.exec.return_value.first.return_value = membership
    session.get.side_effect = lambda model, id: (
        role if model is Role
        else sample_approval if id == sample_approval.id
        else None
    )

    client = _authed_client(admin_user, session)
    try:
        response = client.get(
            f"/api/workspaces/{workspace.id}/approvals/{sample_approval.id}"
        )
        assert response.status_code == 200
        assert response.json()["node_id"] == "approval-123"
    finally:
        _cleanup()


def test_get_approval_not_found(
    admin_user: User, workspace: Workspace, session: MagicMock,
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id,
    )
    session.exec.return_value.first.return_value = membership
    session.get.side_effect = lambda model, id: role if model is Role else None

    client = _authed_client(admin_user, session)
    try:
        fake_id = uuid.uuid4()
        response = client.get(
            f"/api/workspaces/{workspace.id}/approvals/{fake_id}"
        )
        assert response.status_code == 404
    finally:
        _cleanup()


# --- Decide ---


def test_decide_approval_approved(
    admin_user: User,
    workspace: Workspace,
    sample_approval: ApprovalRequest,
    session: MagicMock,
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id,
    )
    required_role = Role(
        id=sample_approval.required_role_id,
        workspace_id=workspace.id,
        name="reviewer",
        is_system=False,
        full_access=False,
        permissions={},
    )

    session.exec.return_value.first.return_value = membership

    def _get_side_effect(model, id):
        if model is Role:
            if id == role.id:
                return role
            if id == required_role.id:
                return required_role
            return role
        if id == sample_approval.id:
            return sample_approval
        return None

    session.get.side_effect = _get_side_effect

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/approvals/{sample_approval.id}/decide",
            json={"decision": "approved", "comment": "Looks good"},
        )
        assert response.status_code == 200
        assert sample_approval.status == "approved"
        assert sample_approval.decided_by == admin_user.id
        assert sample_approval.comment == "Looks good"
    finally:
        _cleanup()


def test_decide_approval_denied(
    admin_user: User,
    workspace: Workspace,
    sample_approval: ApprovalRequest,
    session: MagicMock,
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id,
    )
    required_role = Role(
        id=sample_approval.required_role_id,
        workspace_id=workspace.id,
        name="reviewer",
        is_system=False,
        full_access=False,
        permissions={},
    )

    session.exec.return_value.first.return_value = membership

    def _get_side_effect(model, id):
        if model is Role:
            if id == role.id:
                return role
            if id == required_role.id:
                return required_role
            return role
        if id == sample_approval.id:
            return sample_approval
        return None

    session.get.side_effect = _get_side_effect

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/approvals/{sample_approval.id}/decide",
            json={"decision": "denied", "comment": "Not ready"},
        )
        assert response.status_code == 200
        assert sample_approval.status == "denied"
        assert sample_approval.comment == "Not ready"
    finally:
        _cleanup()


def test_decide_already_decided(
    admin_user: User,
    workspace: Workspace,
    sample_approval: ApprovalRequest,
    session: MagicMock,
) -> None:
    sample_approval.status = "approved"
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=role.id,
    )
    session.exec.return_value.first.return_value = membership
    session.get.side_effect = lambda model, id: (
        role if model is Role
        else sample_approval if id == sample_approval.id
        else None
    )

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/approvals/{sample_approval.id}/decide",
            json={"decision": "denied"},
        )
        assert response.status_code == 409
    finally:
        _cleanup()


def test_decide_wrong_role_forbidden(
    admin_user: User,
    workspace: Workspace,
    sample_approval: ApprovalRequest,
    session: MagicMock,
) -> None:
    viewer_role = _view_only_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id, user_id=admin_user.id, role_id=viewer_role.id,
    )
    # view_only role doesn't have automations.edit, so it should 403 at permission level
    _stub_membership(session, viewer_role)

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/approvals/{sample_approval.id}/decide",
            json={"decision": "approved"},
        )
        assert response.status_code == 403
    finally:
        _cleanup()
