"""Role request/response schemas."""

import uuid
from typing import Any

from pydantic import BaseModel, Field


class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    permissions: dict[str, Any] = Field(default_factory=dict)


class RoleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    permissions: dict[str, Any] | None = None


class RoleRead(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID | None
    name: str
    is_system: bool
    full_access: bool
    permissions: dict[str, Any]
