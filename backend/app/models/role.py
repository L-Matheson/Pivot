"""Role model for system and custom workspace roles."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, SQLModel, UniqueConstraint

from app.models.base import created_at_field, id_field, updated_at_field


class Role(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("workspace_id", "name", name="uq_role_workspace_name"),
    )

    id: uuid.UUID = id_field()
    workspace_id: uuid.UUID | None = Field(default=None, foreign_key="workspace.id", index=True)
    name: str = Field(max_length=100)
    is_system: bool = Field(default=False)
    full_access: bool = Field(default=False)
    permissions: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))
    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()
