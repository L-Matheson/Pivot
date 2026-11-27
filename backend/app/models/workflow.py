"""Workflow model — stores workflow definition as JSONB."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from app.models.base import created_at_field, id_field, updated_at_field


def _empty_definition() -> dict[str, Any]:
    return {"schema_version": 1, "nodes": [], "edges": []}


class Workflow(SQLModel, table=True):
    id: uuid.UUID = id_field()
    workspace_id: uuid.UUID = Field(foreign_key="workspace.id", index=True)
    name: str = Field(max_length=200)
    description: str = Field(default="")
    folder: str | None = Field(default=None, max_length=200)
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSONB, nullable=False))
    definition: dict[str, Any] = Field(
        default_factory=_empty_definition, sa_column=Column(JSONB, nullable=False)
    )
    is_active: bool = Field(default=True)
    is_archived: bool = Field(default=False)
    created_by: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()
