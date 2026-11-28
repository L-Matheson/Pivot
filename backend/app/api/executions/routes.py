"""Execution list and detail routes (workspace-scoped, permission-gated)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import col, select

from app.core.auth import PermissionRequired
from app.core.db import SessionDep
from app.models.execution import NodeExecution, WorkflowExecution

router = APIRouter(prefix="/workspaces/{workspace_id}/executions", tags=["executions"])


@router.get(
    "",
    dependencies=[Depends(PermissionRequired("automations", "view"))],
)
def list_executions(
    workspace_id: uuid.UUID,
    session: SessionDep,
    workflow_id: uuid.UUID | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[dict]:
    stmt = (
        select(WorkflowExecution)
        .where(WorkflowExecution.workspace_id == workspace_id)
    )
    if workflow_id is not None:
        stmt = stmt.where(WorkflowExecution.workflow_id == workflow_id)
    stmt = stmt.order_by(col(WorkflowExecution.created_at).desc()).limit(limit)

    executions = list(session.exec(stmt).all())
    return [
        {
            "id": e.id,
            "workflow_id": e.workflow_id,
            "triggered_by": e.triggered_by,
            "status": e.status,
            "error": e.error,
            "started_at": e.started_at.isoformat() if e.started_at else None,
            "finished_at": e.finished_at.isoformat() if e.finished_at else None,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in executions
    ]


@router.get(
    "/{execution_id}",
    dependencies=[Depends(PermissionRequired("automations", "view"))],
)
def get_execution(
    workspace_id: uuid.UUID,
    execution_id: uuid.UUID,
    session: SessionDep,
) -> dict:
    execution = session.get(WorkflowExecution, execution_id)
    if execution is None or execution.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execution not found.")

    nodes = list(
        session.exec(
            select(NodeExecution)
            .where(NodeExecution.execution_id == execution_id)
        ).all()
    )

    return {
        "id": execution.id,
        "workflow_id": execution.workflow_id,
        "triggered_by": execution.triggered_by,
        "status": execution.status,
        "error": execution.error,
        "started_at": execution.started_at.isoformat() if execution.started_at else None,
        "finished_at": execution.finished_at.isoformat() if execution.finished_at else None,
        "created_at": execution.created_at.isoformat() if execution.created_at else None,
        "nodes": [
            {
                "id": n.id,
                "node_id": n.node_id,
                "node_type": n.node_type,
                "status": n.status,
                "input_data": n.input_data,
                "output_data": n.output_data,
                "error": n.error,
                "duration_ms": n.duration_ms,
                "started_at": n.started_at.isoformat() if n.started_at else None,
                "finished_at": n.finished_at.isoformat() if n.finished_at else None,
            }
            for n in nodes
        ],
    }
