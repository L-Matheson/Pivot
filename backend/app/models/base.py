"""Shared base fields for all table models."""

import uuid
from datetime import datetime

from sqlmodel import Field


def new_uuid() -> uuid.UUID:
    """Generate a new UUID4 for use as a default primary key."""
    return uuid.uuid4()


def utc_now() -> datetime:
    """Return the current UTC time for use as a default timestamp."""
    from datetime import UTC

    return datetime.now(UTC)


# Common field factories — use these in SQLModel table classes:
#
#   class MyModel(SQLModel, table=True):
#       id: uuid.UUID = id_field()
#       created_at: datetime = created_at_field()
#       updated_at: datetime = updated_at_field()


def id_field() -> uuid.UUID:
    """Primary-key UUID field with a generated default."""
    return Field(default_factory=new_uuid, primary_key=True)


def created_at_field() -> datetime:
    """Timestamp set once when the row is created."""
    return Field(default_factory=utc_now)


def updated_at_field() -> datetime:
    """Timestamp updated each time the row is saved."""
    return Field(default_factory=utc_now)
