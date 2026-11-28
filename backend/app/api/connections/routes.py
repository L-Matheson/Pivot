"""Connection CRUD routes (workspace-scoped, permission-gated)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.core.auth import CurrentUserDep, PermissionRequired
from app.core.db import SessionDep
from app.core.encryption import decrypt_credentials, encrypt_credentials
from app.models.connection import Connection
from app.schemas.connection import (
    ConnectionCreate,
    ConnectionListItem,
    ConnectionRead,
)

from .commands import get_workspace_connection
from .utils import require_encryption_key

router = APIRouter(prefix="/workspaces/{workspace_id}/connections", tags=["connections"])


@router.get(
    "",
    response_model=list[ConnectionListItem],
    dependencies=[Depends(PermissionRequired("connections", "view"))],
)
def list_connections(
    workspace_id: uuid.UUID,
    session: SessionDep,
) -> list[Connection]:
    stmt = (
        select(Connection)
        .where(Connection.workspace_id == workspace_id)
        .order_by(Connection.updated_at.desc())  # type: ignore[union-attr]
    )
    return list(session.exec(stmt).all())


@router.post(
    "",
    response_model=ConnectionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionRequired("connections", "manage"))],
)
def create_connection(
    workspace_id: uuid.UUID,
    body: ConnectionCreate,
    session: SessionDep,
    user: CurrentUserDep,
) -> Connection:
    key = require_encryption_key()

    encrypted = None
    if body.credentials:
        encrypted = encrypt_credentials(body.credentials, key)

    connection = Connection(
        workspace_id=workspace_id,
        provider=body.provider,
        name=body.name,
        auth_type=body.auth_type,
        credentials_encrypted=encrypted,
        scopes=body.scopes,
        status="connected",
        connected_by_user_id=user.id,
    )
    session.add(connection)
    session.commit()
    session.refresh(connection)
    return connection


@router.get(
    "/{connection_id}",
    response_model=ConnectionRead,
    dependencies=[Depends(PermissionRequired("connections", "view"))],
)
def get_connection(
    workspace_id: uuid.UUID,
    connection_id: uuid.UUID,
    session: SessionDep,
) -> Connection:
    return get_workspace_connection(session, workspace_id, connection_id)


@router.post(
    "/{connection_id}/test",
    dependencies=[Depends(PermissionRequired("connections", "manage"))],
)
def test_connection(
    workspace_id: uuid.UUID,
    connection_id: uuid.UUID,
    session: SessionDep,
) -> dict:
    conn = get_workspace_connection(session, workspace_id, connection_id)
    key = require_encryption_key()

    if conn.credentials_encrypted is None:
        return {"ok": False, "detail": "No credentials stored."}

    try:
        creds = decrypt_credentials(conn.credentials_encrypted, key)
    except Exception:
        return {"ok": False, "detail": "Failed to decrypt credentials."}

    if conn.auth_type == "oauth2" and "access_token" in creds:
        return {"ok": True, "detail": "Credentials present and decryptable."}

    if conn.auth_type == "api_key" and "api_key" in creds:
        return {"ok": True, "detail": "API key present and decryptable."}

    return {"ok": True, "detail": "Credentials present and decryptable."}


@router.delete(
    "/{connection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionRequired("connections", "manage"))],
)
def delete_connection(
    workspace_id: uuid.UUID,
    connection_id: uuid.UUID,
    session: SessionDep,
) -> None:
    conn = get_workspace_connection(session, workspace_id, connection_id)
    session.delete(conn)
    session.commit()
