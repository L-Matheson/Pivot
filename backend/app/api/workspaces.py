"""Workspace CRUD and membership management routes."""

import uuid

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.core.auth import CurrentUserDep, require_workspace_role
from app.core.db import SessionDep
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMembership, WorkspaceRole
from app.schemas.workspace import (
    MemberAdd,
    MemberRead,
    MemberUpdate,
    WorkspaceCreate,
    WorkspaceRead,
    WorkspaceUpdate,
)

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

    workspace = Workspace(
        name=body.name,
        slug=body.slug,
        owner_user_id=user.id,
    )
    session.add(workspace)

    membership = WorkspaceMembership(
        workspace_id=workspace.id,
        user_id=user.id,
        role=WorkspaceRole.owner,
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
    user: CurrentUserDep,
    session: SessionDep,
) -> Workspace:
    require_workspace_role(session, workspace_id, user, WorkspaceRole.viewer)

    workspace = session.get(Workspace, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found.")
    return workspace


@router.patch("/{workspace_id}", response_model=WorkspaceRead)
def update_workspace(
    workspace_id: uuid.UUID,
    body: WorkspaceUpdate,
    user: CurrentUserDep,
    session: SessionDep,
) -> Workspace:
    require_workspace_role(session, workspace_id, user, WorkspaceRole.owner)

    workspace = session.get(Workspace, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found.")

    if body.name is not None:
        workspace.name = body.name

    session.add(workspace)
    session.commit()
    session.refresh(workspace)
    return workspace


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    workspace_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
) -> None:
    # TODO: replace with soft-delete / archival before production
    require_workspace_role(session, workspace_id, user, WorkspaceRole.owner)

    workspace = session.get(Workspace, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found.")

    memberships = session.exec(
        select(WorkspaceMembership).where(WorkspaceMembership.workspace_id == workspace_id)
    ).all()
    for m in memberships:
        session.delete(m)

    session.delete(workspace)
    session.commit()


@router.get("/{workspace_id}/members")
def list_members(
    workspace_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
) -> list[MemberRead]:
    require_workspace_role(session, workspace_id, user, WorkspaceRole.viewer)

    rows = session.exec(
        select(WorkspaceMembership, User)
        .join(User, User.id == WorkspaceMembership.user_id)
        .where(WorkspaceMembership.workspace_id == workspace_id)
    ).all()

    return [
        MemberRead(
            user_id=membership.user_id,
            email=u.email,
            display_name=u.display_name,
            role=membership.role,
        )
        for membership, u in rows
    ]


@router.post(
    "/{workspace_id}/members",
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    workspace_id: uuid.UUID,
    body: MemberAdd,
    user: CurrentUserDep,
    session: SessionDep,
) -> MemberRead:
    require_workspace_role(session, workspace_id, user, WorkspaceRole.owner)

    # TODO: add dedicated ownership-transfer endpoint
    if body.role == WorkspaceRole.owner:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot add a member as owner.",
        )

    target = session.exec(select(User).where(User.email == body.email)).first()
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with email '{body.email}'.",
        )

    existing = session.exec(
        select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == target.id,
        )
    ).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this workspace.",
        )

    membership = WorkspaceMembership(
        workspace_id=workspace_id,
        user_id=target.id,
        role=body.role,
    )
    session.add(membership)
    session.commit()

    return MemberRead(
        user_id=target.id,
        email=target.email,
        display_name=target.display_name,
        role=membership.role,
    )


@router.patch("/{workspace_id}/members/{member_id}")
def update_member_role(
    workspace_id: uuid.UUID,
    member_id: uuid.UUID,
    body: MemberUpdate,
    user: CurrentUserDep,
    session: SessionDep,
) -> MemberRead:
    require_workspace_role(session, workspace_id, user, WorkspaceRole.owner)

    if body.role == WorkspaceRole.owner:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot promote to owner via this endpoint.",
        )

    membership = session.exec(
        select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == member_id,
        )
    ).first()
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this workspace.",
        )

    if membership.role == WorkspaceRole.owner:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot change the owner's role.",
        )

    membership.role = body.role
    session.add(membership)
    session.commit()

    target = session.get(User, member_id)
    return MemberRead(
        user_id=member_id,
        email=target.email,
        display_name=target.display_name,
        role=membership.role,
    )


@router.delete(
    "/{workspace_id}/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_member(
    workspace_id: uuid.UUID,
    member_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
) -> None:
    require_workspace_role(session, workspace_id, user, WorkspaceRole.owner)

    membership = session.exec(
        select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == member_id,
        )
    ).first()
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this workspace.",
        )

    if membership.role == WorkspaceRole.owner:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot remove the workspace owner.",
        )

    session.delete(membership)
    session.commit()
