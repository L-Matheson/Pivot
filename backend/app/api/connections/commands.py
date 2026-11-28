import uuid

from fastapi import HTTPException, status
from sqlmodel import Session

from app.models.connection import Connection


def get_workspace_connection(
    session: Session,
    workspace_id: uuid.UUID,
    connection_id: uuid.UUID,
) -> Connection:
    conn = session.get(Connection, connection_id)
    if conn is None or conn.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found.",
        )
    return conn
