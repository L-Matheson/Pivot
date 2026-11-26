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
    return create_engine(str(settings.database_url), echo=settings.debug)


def get_session() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
