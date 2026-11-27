"""Workspace and WorkspaceMembership table models."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from app.models.base import created_at_field, id_field, updated_at_field


class Workspace(SQLModel, table=True):
    id: uuid.UUID = id_field()
    name: str = Field(max_length=150)
    slug: str = Field(max_length=80, unique=True, index=True)
    owner_user_id: uuid.UUID = Field(foreign_key="user.id")
    theme_config: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()


class WorkspaceMembership(SQLModel, table=True):
    workspace_id: uuid.UUID = Field(foreign_key="workspace.id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    role_id: uuid.UUID = Field(foreign_key="role.id")
    created_at: datetime = created_at_field()
