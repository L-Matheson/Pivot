"""Workspace request/response schemas."""

import uuid

from pydantic import BaseModel, Field


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    slug: str = Field(
        min_length=1,
        max_length=80,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)


class WorkspaceRead(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    owner_user_id: uuid.UUID


class MemberAdd(BaseModel):
    email: str
    role_id: uuid.UUID


class MemberUpdate(BaseModel):
    role_id: uuid.UUID


class MemberRead(BaseModel):
    user_id: uuid.UUID
    email: str
    display_name: str
    role_id: uuid.UUID
    role_name: str
