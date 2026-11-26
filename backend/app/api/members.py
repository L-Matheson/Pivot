"""Workspace member management routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.core.auth import CurrentUserDep, PermissionRequired
from app.core.db import SessionDep
from app.models.role import Role
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMembership
from app.schemas.workspace import MemberAdd, MemberRead, MemberUpdate

router = APIRouter(prefix="/workspaces/{workspace_id}/members", tags=["members"])


@router.get(
    "",
    response_model=list[MemberRead],
    dependencies=[Depends(PermissionRequired("members", "view"))],
)
def list_members(
    workspace_id: uuid.UUID,
    session: SessionDep,
) -> list[MemberRead]:
    rows = session.exec(
        select(WorkspaceMembership, User, Role)
        .join(User, User.id == WorkspaceMembership.user_id)
        .join(Role, Role.id == WorkspaceMembership.role_id)
        .where(WorkspaceMembership.workspace_id == workspace_id)
    ).all()

    return [
        MemberRead(
            user_id=membership.user_id,
            email=u.email,
            display_name=u.display_name,
            role_id=membership.role_id,
            role_name=role.name,
        )
        for membership, u, role in rows
    ]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionRequired("members", "manage"))],
)
def add_member(
    workspace_id: uuid.UUID,
    body: MemberAdd,
    session: SessionDep,
) -> MemberRead:
    role = session.get(Role, body.role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found.")

    if not role.is_system and role.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Role does not belong to this workspace.",
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
        role_id=body.role_id,
    )
    session.add(membership)
    session.commit()

    return MemberRead(
        user_id=target.id,
        email=target.email,
        display_name=target.display_name,
        role_id=role.id,
        role_name=role.name,
    )


@router.patch(
    "/{member_id}",
    dependencies=[Depends(PermissionRequired("members", "manage"))],
)
def update_member_role(
    workspace_id: uuid.UUID,
    member_id: uuid.UUID,
    body: MemberUpdate,
    session: SessionDep,
) -> MemberRead:
    role = session.get(Role, body.role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found.")

    if not role.is_system and role.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Role does not belong to this workspace.",
        )

    workspace = session.get(Workspace, workspace_id)
    if workspace is not None and workspace.owner_user_id == member_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot change the workspace owner's role.",
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

    membership.role_id = body.role_id
    session.add(membership)
    session.commit()

    target = session.get(User, member_id)
    return MemberRead(
        user_id=member_id,
        email=target.email,
        display_name=target.display_name,
        role_id=role.id,
        role_name=role.name,
    )


@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionRequired("members", "manage"))],
)
def remove_member(
    workspace_id: uuid.UUID,
    member_id: uuid.UUID,
    session: SessionDep,
) -> None:
    workspace = session.get(Workspace, workspace_id)
    if workspace is not None and workspace.owner_user_id == member_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot remove the workspace owner.",
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

    session.delete(membership)
    session.commit()
