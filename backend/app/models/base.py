"""Shared field factories for SQLModel table classes."""

import uuid
from datetime import UTC, datetime

from sqlmodel import Field


def new_uuid() -> uuid.UUID:
    return uuid.uuid4()


def utc_now() -> datetime:
    return datetime.now(UTC)


def id_field() -> uuid.UUID:
    return Field(default_factory=new_uuid, primary_key=True)


def created_at_field() -> datetime:
    return Field(default_factory=utc_now)


def updated_at_field() -> datetime:
    return Field(default_factory=utc_now)
