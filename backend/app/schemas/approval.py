"""Approval request/response schemas."""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ApprovalDecision(str, Enum):
    approved = "approved"
    denied = "denied"


class ApprovalRequestCreate(BaseModel):
    workflow_id: uuid.UUID
    node_id: str = Field(min_length=1)
    required_role_id: uuid.UUID


class ApprovalDecide(BaseModel):
    decision: ApprovalDecision
    comment: str = Field(default="", max_length=2000)


class ApprovalRequestRead(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    workflow_id: uuid.UUID
    node_id: str
    required_role_id: uuid.UUID
    status: str
    decided_by: uuid.UUID | None
    decided_at: datetime | None
    comment: str
    created_at: datetime
    updated_at: datetime
