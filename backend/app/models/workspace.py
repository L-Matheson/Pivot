"""Workspace and WorkspaceMembership table models."""

import enum
import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.base import created_at_field, id_field, updated_at_field


class WorkspaceRole(enum.StrEnum):
    owner = "owner"
    editor = "editor"
    viewer = "viewer"


class Workspace(SQLModel, table=True):
    id: uuid.UUID = id_field()
    name: str = Field(max_length=150)
    slug: str = Field(max_length=80, unique=True, index=True)
    owner_user_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()


class WorkspaceMembership(SQLModel, table=True):
    workspace_id: uuid.UUID = Field(foreign_key="workspace.id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    role: WorkspaceRole = Field()
    created_at: datetime = created_at_field()
