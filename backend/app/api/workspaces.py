"""Workspace CRUD routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.core.auth import CurrentUserDep, PermissionRequired, WorkspaceMemberDep
from app.core.db import SessionDep
from app.models.role import Role
from app.models.workspace import Workspace, WorkspaceMembership
from app.schemas.workspace import WorkspaceCreate, WorkspaceRead, WorkspaceUpdate

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
def create_workspace(
    body: WorkspaceCreate,
    user: CurrentUserDep,
    session: SessionDep,
) -> Workspace:
    existing = session.exec(select(Workspace).where(Workspace.slug == body.slug)).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A workspace with slug '{body.slug}' already exists.",
        )

    workspace = Workspace(name=body.name, slug=body.slug, owner_user_id=user.id)
    session.add(workspace)

    admin_role = session.exec(
        select(Role).where(Role.is_system == True, Role.full_access == True)  # noqa: E712
    ).first()
    if admin_role is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System admin role not found.",
        )

    membership = WorkspaceMembership(
        workspace_id=workspace.id,
        user_id=user.id,
        role_id=admin_role.id,
    )
    session.add(membership)

    session.commit()
    session.refresh(workspace)
    return workspace


@router.get("", response_model=list[WorkspaceRead])
def list_workspaces(user: CurrentUserDep, session: SessionDep) -> list[Workspace]:
    workspaces = session.exec(
        select(Workspace)
        .join(WorkspaceMembership, WorkspaceMembership.workspace_id == Workspace.id)
        .where(WorkspaceMembership.user_id == user.id)
    ).all()
    return list(workspaces)


@router.get("/{workspace_id}", response_model=WorkspaceRead)
def get_workspace(
    workspace_id: uuid.UUID,
    _auth: WorkspaceMemberDep,
    session: SessionDep,
) -> Workspace:
    workspace = session.get(Workspace, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found.")
    return workspace


@router.patch(
    "/{workspace_id}",
    response_model=WorkspaceRead,
    dependencies=[Depends(PermissionRequired("settings", "manage"))],
)
def update_workspace(
    workspace_id: uuid.UUID,
    body: WorkspaceUpdate,
    session: SessionDep,
) -> Workspace:
    workspace = session.get(Workspace, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found.")

    if body.name is not None:
        workspace.name = body.name

    session.add(workspace)
    session.commit()
    session.refresh(workspace)
    return workspace


@router.delete(
    "/{workspace_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionRequired("settings", "manage"))],
)
def delete_workspace(
    workspace_id: uuid.UUID,
    session: SessionDep,
) -> None:
    # TODO: replace with soft-delete / archival before production
    workspace = session.get(Workspace, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found.")

    memberships = session.exec(
        select(WorkspaceMembership).where(WorkspaceMembership.workspace_id == workspace_id)
    ).all()
    for m in memberships:
        session.delete(m)

    custom_roles = session.exec(
        select(Role).where(Role.workspace_id == workspace_id)
    ).all()
    for r in custom_roles:
        session.delete(r)

    session.delete(workspace)
    session.commit()
