"""Workflow execution orchestrator.

Validates the graph, resolves execution order, runs each node in
sequence, propagates outputs, and persists execution state per node.

Branching: when a node's output contains a ``branch`` key (e.g. a
condition node returning ``"yes"`` / ``"no"``), the runner compares it
against each outgoing edge's ``source_handle``.  Edges whose handle
doesn't match are marked inactive, and any node reachable *only*
through inactive edges is skipped.
"""

from __future__ import annotations

import time
import uuid
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

from app.core.graph import topological_sort, validate_definition
from app.engine.base import ExecutionContext, NodeResult, WorkflowRunResult
from app.engine.registry import get_executor
from app.models.execution import NodeExecution, WorkflowExecution
from app.schemas.workflow import WorkflowDefinition, WorkflowEdge


def _build_edge_index(
    edges: list[WorkflowEdge],
) -> tuple[
    dict[str, list[tuple[str, str | None]]],
    dict[str, list[tuple[str, str | None]]],
]:
    """Return (successors, predecessors) keyed by node id.

    Each entry is a list of ``(peer_node_id, source_handle)`` tuples.
    """
    successors: dict[str, list[tuple[str, str | None]]] = defaultdict(list)
    predecessors: dict[str, list[tuple[str, str | None]]] = defaultdict(list)
    for e in edges:
        successors[e.source].append((e.target, e.source_handle))
        predecessors[e.target].append((e.source, e.source_handle))
    return successors, predecessors


def _is_node_reachable(
    node_id: str,
    predecessors: dict[str, list[tuple[str, str | None]]],
    inactive_edges: set[tuple[str, str]],
) -> bool:
    """A node is reachable if it has no predecessors (root) or at least
    one incoming edge is still active."""
    preds = predecessors.get(node_id)
    if not preds:
        return True
    return any((src, node_id) not in inactive_edges for src, _ in preds)


def run_workflow(
    definition: WorkflowDefinition,
    context: ExecutionContext,
    workflow_id: uuid.UUID | None = None,
) -> WorkflowRunResult:
    errors = validate_definition(definition)
    if errors:
        raise ValueError(f"Invalid workflow: {'; '.join(errors)}")

    node_map = {n.id: n for n in definition.nodes}
    edge_tuples = [(e.source, e.target) for e in definition.edges]
    order = topological_sort(list(node_map.keys()), edge_tuples)
    successors, predecessors = _build_edge_index(definition.edges)

    started_at = datetime.now(UTC)

    execution = WorkflowExecution(
        workflow_id=workflow_id or uuid.uuid4(),
        workspace_id=context.workspace_id,
        triggered_by=context.user_id,
        status="running",
        started_at=started_at,
    )
    context.session.add(execution)
    context.session.flush()

    node_rows: dict[str, NodeExecution] = {}
    for node_id in order:
        node = node_map[node_id]
        row = NodeExecution(
            execution_id=execution.id,
            node_id=node_id,
            node_type=node.type,
            status="pending",
        )
        context.session.add(row)
        node_rows[node_id] = row
    context.session.flush()

    outputs: dict[str, dict[str, Any]] = {}
    node_results: list[NodeResult] = []
    overall_status: str = "completed"
    inactive_edges: set[tuple[str, str]] = set()

    for node_id in order:
        node = node_map[node_id]
        row = node_rows[node_id]

        if not _is_node_reachable(node_id, predecessors, inactive_edges):
            result = NodeResult(node_id=node_id, status="skipped")
            row.status = "skipped"
            row.finished_at = datetime.now(UTC)
            context.session.flush()
            node_results.append(result)
            # propagate unreachability to successors
            for succ_id, _ in successors.get(node_id, []):
                inactive_edges.add((node_id, succ_id))
            continue

        executor = get_executor(node.type)

        if executor is None:
            result = NodeResult(
                node_id=node_id,
                status="failed",
                error=f"No executor registered for node type '{node.type}'.",
            )
            row.status = "failed"
            row.error = result.error
            row.finished_at = datetime.now(UTC)
            context.session.flush()

            node_results.append(result)
            overall_status = "failed"
            break

        inputs: dict[str, Any] = {}
        for pred_id, _ in predecessors.get(node_id, []):
            if pred_id in outputs:
                inputs[pred_id] = outputs[pred_id]

        row.status = "running"
        row.input_data = inputs
        row.started_at = datetime.now(UTC)
        context.session.flush()

        t0 = time.monotonic()
        try:
            result = executor.execute(node_id, node.config, inputs, context)
        except Exception as exc:
            result = NodeResult(
                node_id=node_id,
                status="failed",
                error=str(exc),
            )
        result.duration_ms = int((time.monotonic() - t0) * 1000)

        row.status = result.status
        row.output_data = result.output
        row.error = result.error
        row.duration_ms = result.duration_ms
        row.finished_at = datetime.now(UTC)
        context.session.flush()

        node_results.append(result)
        outputs[node_id] = result.output

        if result.status == "failed":
            overall_status = "failed"
            break

        # branching: when a node outputs a branch key, deactivate edges
        # whose source_handle doesn't match
        branch = result.output.get("branch")
        if branch is not None:
            for succ_id, handle in successors.get(node_id, []):
                if handle is not None and handle != branch:
                    inactive_edges.add((node_id, succ_id))

    # mark remaining pending nodes as skipped
    for node_id in order:
        row = node_rows[node_id]
        if row.status == "pending":
            row.status = "skipped"
            row.finished_at = datetime.now(UTC)
    context.session.flush()

    finished_at = datetime.now(UTC)
    execution.status = overall_status
    execution.finished_at = finished_at
    if overall_status == "failed" and node_results:
        last = node_results[-1]
        if last.error:
            execution.error = last.error
    context.session.commit()

    return WorkflowRunResult(
        execution_id=execution.id,
        status=overall_status,  # type: ignore[arg-type]
        node_results=node_results,
        started_at=started_at,
        finished_at=finished_at,
    )
