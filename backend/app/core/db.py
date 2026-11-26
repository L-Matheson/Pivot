"""Database engine, session factory, and FastAPI dependency."""

from collections.abc import Generator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from app.core.config import settings


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Return a lazily-created singleton engine.

    Lazy creation avoids importing the database driver at module load time,
    which lets tests that override ``get_session`` run without Postgres.
    """
    return create_engine(str(settings.database_url), echo=settings.debug)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session and close it after the request."""
    with Session(get_engine()) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
