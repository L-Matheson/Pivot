"""Connection request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ConnectionCreate(BaseModel):
    provider: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    auth_type: str = Field(min_length=1, max_length=30)
    credentials: dict | None = None
    scopes: str = Field(default="")


class ConnectionRead(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    provider: str
    name: str
    auth_type: str
    scopes: str
    status: str
    connected_by_user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ConnectionListItem(BaseModel):
    id: uuid.UUID
    provider: str
    name: str
    auth_type: str
    scopes: str
    status: str
    connected_by_user_id: uuid.UUID
    updated_at: datetime


class OAuthAuthorizeResponse(BaseModel):
    authorize_url: str
    state: str


class OAuthCallbackRequest(BaseModel):
    code: str
    state: str
