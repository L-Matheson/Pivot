"""Authentication and authorization dependencies."""

import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.core.db import SessionDep
from app.core.security import decode_token
from app.models.user import User
from app.models.workspace import WorkspaceMembership, WorkspaceRole

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: SessionDep,
) -> User:
    """Extract and validate the current user from the JWT Bearer token."""
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

ROLE_HIERARCHY: dict[WorkspaceRole, int] = {
    WorkspaceRole.viewer: 1,
    WorkspaceRole.editor: 2,
    WorkspaceRole.owner: 3,
}


def get_membership(
    session: Session,
    workspace_id: uuid.UUID,
    user_id: uuid.UUID,
) -> WorkspaceMembership | None:
    return session.exec(
        select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == user_id,
        )
    ).first()


def require_workspace_role(
    session: Session,
    workspace_id: uuid.UUID,
    user: User,
    minimum_role: WorkspaceRole,
) -> WorkspaceMembership:
    """Assert the user has at least `minimum_role` in the workspace.

    Returns 404 for non-members to avoid leaking workspace existence.
    """
    membership = get_membership(session, workspace_id, user.id)

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found.",
        )

    user_level = ROLE_HIERARCHY[membership.role]
    required_level = ROLE_HIERARCHY[minimum_role]

    if user_level < required_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Requires '{minimum_role.value}' role or higher.",
        )

    return membership
