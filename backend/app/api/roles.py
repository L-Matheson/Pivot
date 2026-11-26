"""Custom role CRUD routes (workspace-scoped, permission-gated)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.core.auth import PermissionRequired
from app.core.db import SessionDep
from app.models.role import Role
from app.models.workspace import WorkspaceMembership
from app.schemas.role import RoleCreate, RoleRead, RoleUpdate

router = APIRouter(prefix="/workspaces/{workspace_id}/roles", tags=["roles"])


@router.get(
    "",
    response_model=list[RoleRead],
    dependencies=[Depends(PermissionRequired("roles", "view"))],
)
def list_roles(
    workspace_id: uuid.UUID,
    session: SessionDep,
) -> list[Role]:
    roles = session.exec(
        select(Role).where(
            (Role.workspace_id == workspace_id) | (Role.is_system == True)  # noqa: E712
        )
    ).all()
    return list(roles)


@router.post(
    "",
    response_model=RoleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionRequired("roles", "manage"))],
)
def create_role(
    workspace_id: uuid.UUID,
    body: RoleCreate,
    session: SessionDep,
) -> Role:
    existing = session.exec(
        select(Role).where(Role.workspace_id == workspace_id, Role.name == body.name)
    ).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A role named '{body.name}' already exists in this workspace.",
        )

    role = Role(
        workspace_id=workspace_id,
        name=body.name,
        is_system=False,
        full_access=False,
        permissions=body.permissions,
    )
    session.add(role)
    session.commit()
    session.refresh(role)
    return role


@router.get(
    "/{role_id}",
    response_model=RoleRead,
    dependencies=[Depends(PermissionRequired("roles", "view"))],
)
def get_role(
    workspace_id: uuid.UUID,
    role_id: uuid.UUID,
    session: SessionDep,
) -> Role:
    role = session.get(Role, role_id)
    if role is None or (not role.is_system and role.workspace_id != workspace_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found.")
    return role


@router.patch(
    "/{role_id}",
    response_model=RoleRead,
    dependencies=[Depends(PermissionRequired("roles", "manage"))],
)
def update_role(
    workspace_id: uuid.UUID,
    role_id: uuid.UUID,
    body: RoleUpdate,
    session: SessionDep,
) -> Role:
    role = session.get(Role, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found.")

    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="System roles cannot be modified.",
        )

    if role.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found.")

    if body.name is not None:
        role.name = body.name
    if body.permissions is not None:
        role.permissions = body.permissions

    session.add(role)
    session.commit()
    session.refresh(role)
    return role


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionRequired("roles", "manage"))],
)
def delete_role(
    workspace_id: uuid.UUID,
    role_id: uuid.UUID,
    session: SessionDep,
) -> None:
    role = session.get(Role, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found.")

    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="System roles cannot be deleted.",
        )

    if role.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found.")

    in_use = session.exec(
        select(WorkspaceMembership).where(WorkspaceMembership.role_id == role_id)
    ).first()
    if in_use is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a role that is assigned to members.",
        )

    session.delete(role)
    session.commit()
