"""Execution engine tests — topological sort, executors, runner, endpoint."""

import uuid
from unittest.mock import MagicMock, patch

import pytest  # noqa: F401
from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.core.db import get_session
from app.core.graph import topological_sort
from app.core.security import hash_password
from app.engine.base import ExecutionContext, NodeResult
from app.engine.executors.condition import ConditionExecutor
from app.engine.executors.http_request import HttpRequestExecutor, _is_blocked_url
from app.engine.executors.manual_trigger import ManualTriggerExecutor
from app.engine.executors.send_notification import SendNotificationExecutor
from app.engine.executors.transform import TransformExecutor
from app.main import app
from app.models.role import Role
from app.models.user import User
from app.models.workflow import Workflow
from app.models.workspace import Workspace, WorkspaceMembership
from app.schemas.workflow import WorkflowDefinition  # noqa: F401

# --- Helpers ---


def _admin_role() -> Role:
    return Role(
        id=uuid.uuid4(),
        workspace_id=None,
        name="admin",
        is_system=True,
        full_access=True,
        permissions={},
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


# --- Topological sort ---


def test_topological_sort_linear_chain() -> None:
    order = topological_sort(["a", "b", "c"], [("a", "b"), ("b", "c")])
    assert order == ["a", "b", "c"]


def test_topological_sort_diamond() -> None:
    order = topological_sort(
        ["a", "b", "c", "d"],
        [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")],
    )
    assert order.index("a") < order.index("b")
    assert order.index("a") < order.index("c")
    assert order.index("b") < order.index("d")
    assert order.index("c") < order.index("d")


def test_topological_sort_single_node() -> None:
    order = topological_sort(["x"], [])
    assert order == ["x"]


def test_topological_sort_disconnected() -> None:
    order = topological_sort(["a", "b", "c"], [("a", "b")])
    assert "c" in order
    assert order.index("a") < order.index("b")


# --- Manual trigger executor ---


def test_manual_trigger_executor() -> None:
    user_id = uuid.uuid4()
    ctx = ExecutionContext(
        workspace_id=uuid.uuid4(),
        user_id=user_id,
        session=MagicMock(),
        encryption_key="test-key",
    )
    executor = ManualTriggerExecutor()
    result = executor.execute("t1", {}, {}, ctx)
    assert result.status == "completed"
    assert result.output["triggered"] is True
    assert result.output["triggered_by"] == str(user_id)


# --- Runner ---


@patch("app.engine.runner.get_executor")
def test_runner_executes_in_order(mock_get_executor: MagicMock) -> None:
    from app.engine.runner import run_workflow

    call_order: list[str] = []

    def make_executor(slug: str) -> MagicMock:
        executor = MagicMock()

        def side_effect(node_id: str, config: dict, inputs: dict, ctx: object) -> NodeResult:
            call_order.append(node_id)
            return NodeResult(
                node_id=node_id,
                status="completed",
                output={"from": node_id},
            )

        executor.execute.side_effect = side_effect
        return executor

    executors = {"trigger": make_executor("trigger"), "action": make_executor("action")}
    mock_get_executor.side_effect = lambda slug: executors.get(slug)

    definition = WorkflowDefinition(
        schema_version=1,
        nodes=[
            {"id": "t1", "type": "trigger", "position": {"x": 0, "y": 0}},
            {"id": "a1", "type": "action", "position": {"x": 0, "y": 100}},
        ],
        edges=[{"id": "e1", "source": "t1", "target": "a1"}],
    )

    ctx = ExecutionContext(
        workspace_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        session=MagicMock(),
        encryption_key="test-key",
    )
    result = run_workflow(definition, ctx)
    assert result.status == "completed"
    assert call_order == ["t1", "a1"]
    assert len(result.node_results) == 2


@patch("app.engine.runner.get_executor")
def test_runner_stops_on_failure(mock_get_executor: MagicMock) -> None:
    from app.engine.runner import run_workflow

    trigger_exec = MagicMock()
    trigger_exec.execute.return_value = NodeResult(
        node_id="t1", status="failed", error="boom"
    )
    mock_get_executor.return_value = trigger_exec

    definition = WorkflowDefinition(
        schema_version=1,
        nodes=[
            {"id": "t1", "type": "trigger", "position": {"x": 0, "y": 0}},
            {"id": "a1", "type": "action", "position": {"x": 0, "y": 100}},
        ],
        edges=[{"id": "e1", "source": "t1", "target": "a1"}],
    )

    ctx = ExecutionContext(
        workspace_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        session=MagicMock(),
        encryption_key="test-key",
    )
    result = run_workflow(definition, ctx)
    assert result.status == "failed"
    assert len(result.node_results) == 1


@patch("app.engine.runner.get_executor")
def test_runner_unknown_executor(mock_get_executor: MagicMock) -> None:
    from app.engine.runner import run_workflow

    mock_get_executor.return_value = None

    definition = WorkflowDefinition(
        schema_version=1,
        nodes=[{"id": "t1", "type": "unknown", "position": {"x": 0, "y": 0}}],
        edges=[],
    )

    ctx = ExecutionContext(
        workspace_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        session=MagicMock(),
        encryption_key="test-key",
    )
    result = run_workflow(definition, ctx)
    assert result.status == "failed"
    assert "No executor" in result.node_results[0].error


# --- Run endpoint ---


@patch("app.api.workflows.routes.run_workflow")
@patch("app.api.workflows.routes.settings")
def test_run_workflow_endpoint(
    mock_settings: MagicMock,
    mock_run: MagicMock,
    admin_user: User,
    workspace: Workspace,
    session: MagicMock,
) -> None:
    from datetime import UTC, datetime

    mock_settings.encryption_key = "test-key"

    workflow = Workflow(
        id=uuid.uuid4(),
        workspace_id=workspace.id,
        name="Test",
        created_by=admin_user.id,
        definition={
            "schema_version": 1,
            "nodes": [
                {"id": "t1", "type": "manual_trigger", "position": {"x": 0, "y": 0}, "config": {}}
            ],
            "edges": [],
        },
    )

    from app.engine.base import WorkflowRunResult

    mock_run.return_value = WorkflowRunResult(
        execution_id=uuid.uuid4(),
        status="completed",
        node_results=[
            NodeResult(node_id="t1", status="completed", output={"triggered": True})
        ],
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
    )

    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id,
        user_id=admin_user.id,
        role_id=role.id,
    )
    session.exec.return_value.first.return_value = membership
    session.get.side_effect = lambda model, id: (
        role if model is Role else workflow if id == workflow.id else None
    )

    client = _authed_client(admin_user, session)
    try:
        response = client.post(
            f"/api/workspaces/{workspace.id}/workflows/{workflow.id}/run"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert len(data["node_results"]) == 1
        assert data["node_results"][0]["node_id"] == "t1"
    finally:
        _cleanup()


# --- Condition executor ---


def test_condition_eq_true() -> None:
    ctx = ExecutionContext(
        workspace_id=uuid.uuid4(), user_id=uuid.uuid4(),
        session=MagicMock(), encryption_key="k",
    )
    result = ConditionExecutor().execute(
        "c1",
        {"field": "status", "operator": "eq", "value": "active"},
        {"prev": {"status": "active"}},
        ctx,
    )
    assert result.status == "completed"
    assert result.output["result"] is True
    assert result.output["branch"] == "yes"


def test_condition_eq_false() -> None:
    ctx = ExecutionContext(
        workspace_id=uuid.uuid4(), user_id=uuid.uuid4(),
        session=MagicMock(), encryption_key="k",
    )
    result = ConditionExecutor().execute(
        "c1",
        {"field": "status", "operator": "eq", "value": "active"},
        {"prev": {"status": "inactive"}},
        ctx,
    )
    assert result.output["result"] is False
    assert result.output["branch"] == "no"


def test_condition_contains() -> None:
    ctx = ExecutionContext(
        workspace_id=uuid.uuid4(), user_id=uuid.uuid4(),
        session=MagicMock(), encryption_key="k",
    )
    result = ConditionExecutor().execute(
        "c1",
        {"field": "subject", "operator": "contains", "value": "urgent"},
        {"prev": {"subject": "URGENT: server down"}},
        ctx,
    )
    assert result.output["result"] is True


# --- HTTP Request executor ---


def test_http_request_blocked_url() -> None:
    assert _is_blocked_url("http://localhost:8080/api") is True
    assert _is_blocked_url("http://127.0.0.1/secret") is True
    assert _is_blocked_url("http://192.168.1.1/admin") is True
    assert _is_blocked_url("http://metadata.google.internal/v1") is True
    assert _is_blocked_url("https://example.com/api") is False


def test_http_request_missing_url() -> None:
    ctx = ExecutionContext(
        workspace_id=uuid.uuid4(), user_id=uuid.uuid4(),
        session=MagicMock(), encryption_key="k",
    )
    result = HttpRequestExecutor().execute("h1", {}, {}, ctx)
    assert result.status == "failed"
    assert "URL is required" in result.error


def test_http_request_blocked() -> None:
    ctx = ExecutionContext(
        workspace_id=uuid.uuid4(), user_id=uuid.uuid4(),
        session=MagicMock(), encryption_key="k",
    )
    result = HttpRequestExecutor().execute(
        "h1", {"url": "http://localhost:9999/secret"}, {}, ctx,
    )
    assert result.status == "failed"
    assert "blocked" in result.error.lower()


# --- Send Notification executor ---


def test_send_notification_success() -> None:
    ctx = ExecutionContext(
        workspace_id=uuid.uuid4(), user_id=uuid.uuid4(),
        session=MagicMock(), encryption_key="k",
    )
    result = SendNotificationExecutor().execute(
        "n1", {"message": "Build passed", "channel": "slack"}, {}, ctx,
    )
    assert result.status == "completed"
    assert result.output["delivered"] is True
    assert result.output["channel"] == "slack"


def test_send_notification_missing_message() -> None:
    ctx = ExecutionContext(
        workspace_id=uuid.uuid4(), user_id=uuid.uuid4(),
        session=MagicMock(), encryption_key="k",
    )
    result = SendNotificationExecutor().execute("n1", {}, {}, ctx)
    assert result.status == "failed"


# --- Transform executor ---


def test_transform_passthrough() -> None:
    ctx = ExecutionContext(
        workspace_id=uuid.uuid4(), user_id=uuid.uuid4(),
        session=MagicMock(), encryption_key="k",
    )
    result = TransformExecutor().execute(
        "t1", {"operation": "passthrough"},
        {"prev": {"a": 1, "b": 2}}, ctx,
    )
    assert result.status == "completed"
    assert result.output["data"] == {"a": 1, "b": 2}


def test_transform_map() -> None:
    ctx = ExecutionContext(
        workspace_id=uuid.uuid4(), user_id=uuid.uuid4(),
        session=MagicMock(), encryption_key="k",
    )
    result = TransformExecutor().execute(
        "t1",
        {"operation": "map", "mapping": {"full_name": "name", "years": "age"}},
        {"prev": {"name": "Alice", "age": 30, "extra": "x"}},
        ctx,
    )
    assert result.status == "completed"
    assert result.output["data"] == {"full_name": "Alice", "years": 30}


def test_transform_pick() -> None:
    ctx = ExecutionContext(
        workspace_id=uuid.uuid4(), user_id=uuid.uuid4(),
        session=MagicMock(), encryption_key="k",
    )
    result = TransformExecutor().execute(
        "t1",
        {"operation": "pick", "fields": ["name"]},
        {"prev": {"name": "Alice", "age": 30}},
        ctx,
    )
    assert result.output["data"] == {"name": "Alice"}


def test_transform_filter() -> None:
    ctx = ExecutionContext(
        workspace_id=uuid.uuid4(), user_id=uuid.uuid4(),
        session=MagicMock(), encryption_key="k",
    )
    rows = [{"status": "active", "id": 1}, {"status": "inactive", "id": 2}]
    result = TransformExecutor().execute(
        "t1",
        {"operation": "filter", "field": "status", "value": "active"},
        {"prev": rows},
        ctx,
    )
    assert result.output["data"] == [{"status": "active", "id": 1}]


# --- Branching runner ---


@patch("app.engine.runner.get_executor")
def test_runner_condition_branching(mock_get_executor: MagicMock) -> None:
    """Condition → yes branch runs, no branch is skipped."""
    from app.engine.runner import run_workflow

    call_order: list[str] = []

    def make_executor(output: dict) -> MagicMock:
        executor = MagicMock()

        def side_effect(node_id: str, config: dict, inputs: dict, ctx: object) -> NodeResult:
            call_order.append(node_id)
            return NodeResult(node_id=node_id, status="completed", output=output)

        executor.execute.side_effect = side_effect
        return executor

    cond_exec = make_executor({"result": True, "branch": "yes"})
    yes_exec = make_executor({"done": True})
    no_exec = make_executor({"done": True})

    def lookup(slug: str) -> MagicMock:
        return {"trigger": make_executor({"triggered": True}),
                "condition": cond_exec, "yes_action": yes_exec,
                "no_action": no_exec}.get(slug)

    mock_get_executor.side_effect = lookup

    definition = WorkflowDefinition(
        schema_version=1,
        nodes=[
            {"id": "t1", "type": "trigger", "position": {"x": 0, "y": 0}},
            {"id": "c1", "type": "condition", "position": {"x": 0, "y": 100}},
            {"id": "yes1", "type": "yes_action", "position": {"x": -100, "y": 200}},
            {"id": "no1", "type": "no_action", "position": {"x": 100, "y": 200}},
        ],
        edges=[
            {"id": "e1", "source": "t1", "target": "c1"},
            {"id": "e2", "source": "c1", "target": "yes1", "source_handle": "yes"},
            {"id": "e3", "source": "c1", "target": "no1", "source_handle": "no"},
        ],
    )

    ctx = ExecutionContext(
        workspace_id=uuid.uuid4(), user_id=uuid.uuid4(),
        session=MagicMock(), encryption_key="k",
    )
    result = run_workflow(definition, ctx)
    assert result.status == "completed"
    assert "yes1" in call_order
    assert "no1" not in call_order
    skipped = [nr for nr in result.node_results if nr.status == "skipped"]
    assert any(nr.node_id == "no1" for nr in skipped)


# --- Existing endpoint tests ---


def test_run_workflow_not_found(
    admin_user: User, workspace: Workspace, session: MagicMock
) -> None:
    role = _admin_role()
    membership = WorkspaceMembership(
        workspace_id=workspace.id,
        user_id=admin_user.id,
        role_id=role.id,
    )
    session.exec.return_value.first.return_value = membership
    session.get.side_effect = lambda model, id: role if model is Role else None

    client = _authed_client(admin_user, session)
    try:
        fake_id = uuid.uuid4()
        response = client.post(
            f"/api/workspaces/{workspace.id}/workflows/{fake_id}/run"
        )
        assert response.status_code == 404
    finally:
        _cleanup()
