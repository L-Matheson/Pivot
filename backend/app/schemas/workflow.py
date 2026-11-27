"""Workflow request/response schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# --- Definition sub-schemas ---


class NodePosition(BaseModel):
    x: float
    y: float


class WorkflowNode(BaseModel):
    id: str = Field(min_length=1)
    type: str = Field(min_length=1)
    position: NodePosition
    config: dict[str, Any] = Field(default_factory=dict)


class WorkflowEdge(BaseModel):
    id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    target: str = Field(min_length=1)
    source_handle: str | None = None


class WorkflowDefinition(BaseModel):
    schema_version: int = 1
    nodes: list[WorkflowNode] = Field(default_factory=list)
    edges: list[WorkflowEdge] = Field(default_factory=list)


# --- CRUD schemas ---


class WorkflowCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)


class WorkflowUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    folder: str | None = None
    tags: list[str] | None = None
    definition: WorkflowDefinition | None = None
    is_active: bool | None = None


class WorkflowRead(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    description: str
    folder: str | None
    tags: list[str]
    definition: dict[str, Any]
    is_active: bool
    is_archived: bool
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime


class WorkflowListItem(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    is_active: bool
    is_archived: bool
    folder: str | None
    tags: list[str]
    created_by: uuid.UUID
    updated_at: datetime
