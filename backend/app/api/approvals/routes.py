"""Approval request routes (workspace-scoped, permission-gated)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select

from app.core.auth import CurrentUserDep, PermissionRequired
from app.core.db import SessionDep
from app.models.approval import ApprovalRequest, ApprovalStatus
from app.models.base import utc_now
from app.models.role import Role
from app.models.workspace import WorkspaceMembership
from app.schemas.approval import (
    ApprovalDecide,
    ApprovalRequestCreate,
    ApprovalRequestRead,
)

router = APIRouter(prefix="/workspaces/{workspace_id}/approvals", tags=["approvals"])


@router.get(
    "",
    response_model=list[ApprovalRequestRead],
    dependencies=[Depends(PermissionRequired("automations", "view"))],
)
def list_approvals(
    workspace_id: uuid.UUID,
    session: SessionDep,
    status_filter: str | None = Query(default=None, alias="status"),
) -> list[ApprovalRequest]:
    stmt = select(ApprovalRequest).where(
        ApprovalRequest.workspace_id == workspace_id
    )
    if status_filter:
        stmt = stmt.where(ApprovalRequest.status == status_filter)
    stmt = stmt.order_by(ApprovalRequest.created_at.desc())  # type: ignore[union-attr]
    return list(session.exec(stmt).all())


@router.post(
    "",
    response_model=ApprovalRequestRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionRequired("automations", "edit"))],
)
def create_approval(
    workspace_id: uuid.UUID,
    body: ApprovalRequestCreate,
    session: SessionDep,
) -> ApprovalRequest:
    role = session.get(Role, body.required_role_id)
    if role is None or (not role.is_system and role.workspace_id != workspace_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found in this workspace.",
        )

    approval = ApprovalRequest(
        workspace_id=workspace_id,
        workflow_id=body.workflow_id,
        node_id=body.node_id,
        required_role_id=body.required_role_id,
    )
    session.add(approval)
    session.commit()
    session.refresh(approval)
    return approval


@router.get(
    "/{approval_id}",
    response_model=ApprovalRequestRead,
    dependencies=[Depends(PermissionRequired("automations", "view"))],
)
def get_approval(
    workspace_id: uuid.UUID,
    approval_id: uuid.UUID,
    session: SessionDep,
) -> ApprovalRequest:
    approval = session.get(ApprovalRequest, approval_id)
    if approval is None or approval.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found.",
        )
    return approval


@router.post(
    "/{approval_id}/decide",
    response_model=ApprovalRequestRead,
    dependencies=[Depends(PermissionRequired("automations", "edit"))],
)
def decide_approval(
    workspace_id: uuid.UUID,
    approval_id: uuid.UUID,
    body: ApprovalDecide,
    session: SessionDep,
    user: CurrentUserDep,
) -> ApprovalRequest:
    approval = session.get(ApprovalRequest, approval_id)
    if approval is None or approval.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found.",
        )

    if approval.status != ApprovalStatus.pending.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Approval already {approval.status}.",
        )

    membership = session.exec(
        select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == user.id,
        )
    ).first()
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a workspace member.")

    required_role = session.get(Role, approval.required_role_id)
    if required_role is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Required role not found.",
        )

    user_role = session.get(Role, membership.role_id)
    if user_role is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User role not found.",
        )

    if membership.role_id != approval.required_role_id and not user_role.full_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Only members with the '{required_role.name}' role can decide this approval.",
        )

    approval.status = body.decision.value
    approval.decided_by = user.id
    approval.decided_at = utc_now()
    approval.comment = body.comment
    approval.updated_at = utc_now()
    session.add(approval)
    session.commit()
    session.refresh(approval)
    return approval
