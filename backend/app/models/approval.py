"""Approval request model — tracks human approval decisions for workflow nodes."""

import uuid
from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel

from app.models.base import created_at_field, id_field, updated_at_field


class ApprovalStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    denied = "denied"


class ApprovalRequest(SQLModel, table=True):
    __tablename__ = "approvalrequest"

    id: uuid.UUID = id_field()
    workspace_id: uuid.UUID = Field(foreign_key="workspace.id", index=True)
    workflow_id: uuid.UUID = Field(foreign_key="workflow.id", index=True)
    node_id: str = Field(max_length=200)
    required_role_id: uuid.UUID = Field(foreign_key="role.id")
    status: str = Field(default=ApprovalStatus.pending.value, max_length=20)
    decided_by: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    decided_at: datetime | None = Field(default=None)
    comment: str = Field(default="")
    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()
