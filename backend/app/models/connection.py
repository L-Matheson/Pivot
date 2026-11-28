"""Connection model — stores encrypted credentials for external service integrations."""

import uuid
from datetime import datetime

from sqlalchemy import Column, LargeBinary
from sqlmodel import Field, SQLModel

from app.models.base import created_at_field, id_field, updated_at_field


class Connection(SQLModel, table=True):
    id: uuid.UUID = id_field()
    workspace_id: uuid.UUID = Field(foreign_key="workspace.id", index=True)
    provider: str = Field(max_length=50, index=True)
    name: str = Field(max_length=200)
    auth_type: str = Field(max_length=30)
    credentials_encrypted: bytes | None = Field(
        default=None, sa_column=Column(LargeBinary, nullable=True)
    )
    scopes: str = Field(default="")
    status: str = Field(default="connected", max_length=30)
    connected_by_user_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()
