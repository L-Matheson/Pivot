"""Authentication and authorization dependencies."""

import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import select

from app.core.db import SessionDep
from app.core.permissions import check_permission
from app.core.security import decode_token
from app.models.role import Role
from app.models.user import User
from app.models.workspace import WorkspaceMembership

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: SessionDep,
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = uuid.UUID(user_id)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    user = session.get(User, user_uuid)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def _get_membership(
    session: SessionDep,
    workspace_id: uuid.UUID,
    user_id: uuid.UUID,
) -> WorkspaceMembership | None:
    return session.exec(
        select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == user_id,
        )
    ).first()


def _get_member_role(session: SessionDep, membership: WorkspaceMembership) -> Role:
    role = session.get(Role, membership.role_id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Role not found for membership.",
        )
    return role


class WorkspaceMemberRequired:
    """Validates the caller is a member of the workspace."""

    def __call__(
        self,
        workspace_id: uuid.UUID,
        session: SessionDep,
        user: CurrentUserDep,
    ) -> tuple[WorkspaceMembership, Role]:
        membership = _get_membership(session, workspace_id, user.id)
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found.",
            )
        role = _get_member_role(session, membership)
        return membership, role


class PermissionRequired:
    """Validates the caller has a specific permission in the workspace."""

    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action

    def __call__(
        self,
        workspace_id: uuid.UUID,
        session: SessionDep,
        user: CurrentUserDep,
    ) -> tuple[WorkspaceMembership, Role]:
        membership = _get_membership(session, workspace_id, user.id)
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found.",
            )
        role = _get_member_role(session, membership)
        if not check_permission(role, self.resource, self.action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {self.resource}.{self.action}",
            )
        return membership, role


WorkspaceMemberDep = Annotated[
    tuple[WorkspaceMembership, Role], Depends(WorkspaceMemberRequired())
]
