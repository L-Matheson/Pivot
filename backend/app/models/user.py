"""User table model."""

import uuid
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from app.models.base import created_at_field, id_field, updated_at_field


class User(SQLModel, table=True):
    id: uuid.UUID = id_field()
    email: EmailStr = Field(unique=True, index=True)
    password_hash: str = Field()
    display_name: str = Field(max_length=150)
    is_active: bool = Field(default=True)
    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()
