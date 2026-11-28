"""Workflow CRUD routes (workspace-scoped, permission-gated)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select

from app.core.auth import CurrentUserDep, PermissionRequired
from app.core.config import settings
from app.core.db import SessionDep
from app.core.graph import validate_definition
from app.engine import run_workflow
from app.engine.base import ExecutionContext
from app.models.base import utc_now
from app.models.workflow import Workflow
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowDefinition,
    WorkflowListItem,
    WorkflowRead,
    WorkflowRunResponse,
    WorkflowUpdate,
)

router = APIRouter(prefix="/workspaces/{workspace_id}/workflows", tags=["workflows"])


@router.get(
    "",
    response_model=list[WorkflowListItem],
    dependencies=[Depends(PermissionRequired("automations", "view"))],
)
def list_workflows(
    workspace_id: uuid.UUID,
    session: SessionDep,
    archived: bool = Query(default=False),
) -> list[Workflow]:
    stmt = select(Workflow).where(Workflow.workspace_id == workspace_id)
    if not archived:
        stmt = stmt.where(Workflow.is_archived == False)  # noqa: E712
    stmt = stmt.order_by(Workflow.updated_at.desc())  # type: ignore[union-attr]
    return list(session.exec(stmt).all())


@router.post(
    "",
    response_model=WorkflowRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionRequired("automations", "edit"))],
)
def create_workflow(
    workspace_id: uuid.UUID,
    body: WorkflowCreate,
    session: SessionDep,
    user: CurrentUserDep,
) -> Workflow:
    workflow = Workflow(
        workspace_id=workspace_id,
        name=body.name,
        description=body.description,
        created_by=user.id,
    )
    session.add(workflow)
    session.commit()
    session.refresh(workflow)
    return workflow


@router.get(
    "/{workflow_id}",
    response_model=WorkflowRead,
    dependencies=[Depends(PermissionRequired("automations", "view"))],
)
def get_workflow(
    workspace_id: uuid.UUID,
    workflow_id: uuid.UUID,
    session: SessionDep,
) -> Workflow:
    workflow = session.get(Workflow, workflow_id)
    if workflow is None or workflow.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found.")
    return workflow


@router.patch(
    "/{workflow_id}",
    response_model=WorkflowRead,
    dependencies=[Depends(PermissionRequired("automations", "edit"))],
)
def update_workflow(
    workspace_id: uuid.UUID,
    workflow_id: uuid.UUID,
    body: WorkflowUpdate,
    session: SessionDep,
) -> Workflow:
    workflow = session.get(Workflow, workflow_id)
    if workflow is None or workflow.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found.")

    if body.definition is not None:
        errors = validate_definition(body.definition)
        if errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"validation_errors": errors},
            )

    if body.name is not None:
        workflow.name = body.name
    if body.description is not None:
        workflow.description = body.description
    if body.folder is not None:
        workflow.folder = body.folder
    if body.tags is not None:
        workflow.tags = body.tags
    if body.definition is not None:
        workflow.definition = body.definition.model_dump()
    if body.is_active is not None:
        workflow.is_active = body.is_active

    workflow.updated_at = utc_now()
    session.add(workflow)
    session.commit()
    session.refresh(workflow)
    return workflow


@router.post(
    "/{workflow_id}/duplicate",
    response_model=WorkflowRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionRequired("automations", "edit"))],
)
def duplicate_workflow(
    workspace_id: uuid.UUID,
    workflow_id: uuid.UUID,
    session: SessionDep,
    user: CurrentUserDep,
) -> Workflow:
    original = session.get(Workflow, workflow_id)
    if original is None or original.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found.")

    copy = Workflow(
        workspace_id=workspace_id,
        name=f"{original.name} (copy)",
        description=original.description,
        folder=original.folder,
        tags=list(original.tags) if original.tags else [],
        definition=dict(original.definition) if original.definition else {"schema_version": 1, "nodes": [], "edges": []},
        is_active=False,
        created_by=user.id,
    )
    session.add(copy)
    session.commit()
    session.refresh(copy)
    return copy


@router.post(
    "/{workflow_id}/archive",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionRequired("automations", "manage"))],
)
def archive_workflow(
    workspace_id: uuid.UUID,
    workflow_id: uuid.UUID,
    session: SessionDep,
) -> None:
    workflow = session.get(Workflow, workflow_id)
    if workflow is None or workflow.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found.")

    workflow.is_archived = True
    workflow.updated_at = utc_now()
    session.add(workflow)
    session.commit()


@router.delete(
    "/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionRequired("automations", "manage"))],
)
def delete_workflow(
    workspace_id: uuid.UUID,
    workflow_id: uuid.UUID,
    session: SessionDep,
) -> None:
    workflow = session.get(Workflow, workflow_id)
    if workflow is None or workflow.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found.")

    session.delete(workflow)
    session.commit()


@router.post(
    "/{workflow_id}/run",
    dependencies=[Depends(PermissionRequired("automations", "edit"))],
)
def run_workflow_endpoint(
    workspace_id: uuid.UUID,
    workflow_id: uuid.UUID,
    session: SessionDep,
    user: CurrentUserDep,
) -> WorkflowRunResponse:
    workflow = session.get(Workflow, workflow_id)
    if workflow is None or workflow.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found.",
        )

    definition = WorkflowDefinition.model_validate(workflow.definition)
    errors = validate_definition(definition)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"validation_errors": errors},
        )

    ctx = ExecutionContext(
        workspace_id=workspace_id,
        user_id=user.id,
        session=session,
        encryption_key=settings.encryption_key,
    )
    result = run_workflow(definition, ctx, workflow_id=workflow_id)

    return WorkflowRunResponse(
        execution_id=result.execution_id,
        status=result.status,
        node_results=[
            {
                "node_id": nr.node_id,
                "status": nr.status,
                "output": nr.output,
                "error": nr.error,
                "duration_ms": nr.duration_ms,
            }
            for nr in result.node_results
        ],
        started_at=result.started_at,
        finished_at=result.finished_at,
    )
