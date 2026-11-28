"""Execution models — tracks workflow runs and per-node results."""

import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Column, Field, SQLModel
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import created_at_field, id_field, updated_at_field


class WorkflowExecution(SQLModel, table=True):
    __tablename__ = "workflowexecution"

    id: uuid.UUID = id_field()
    workflow_id: uuid.UUID = Field(foreign_key="workflow.id", index=True)
    workspace_id: uuid.UUID = Field(foreign_key="workspace.id", index=True)
    triggered_by: uuid.UUID = Field(foreign_key="user.id")
    status: str = Field(default="running", max_length=30)
    error: str | None = Field(default=None)
    started_at: datetime = created_at_field()
    finished_at: datetime | None = Field(default=None)
    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()


class NodeExecution(SQLModel, table=True):
    __tablename__ = "nodeexecution"

    id: uuid.UUID = id_field()
    execution_id: uuid.UUID = Field(foreign_key="workflowexecution.id", index=True)
    node_id: str = Field(max_length=200)
    node_type: str = Field(max_length=100)
    status: str = Field(default="pending", max_length=30)
    input_data: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False, server_default="{}"))
    output_data: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False, server_default="{}"))
    error: str | None = Field(default=None)
    duration_ms: int = Field(default=0)
    started_at: datetime | None = Field(default=None)
    finished_at: datetime | None = Field(default=None)
