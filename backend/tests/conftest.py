"""Shared test fixtures.

All tests run against a dedicated ``pivot_test`` database.  The env-var
override below fires before any app code is imported, so the engine,
settings, and Alembic all see the test URL — never the production one.

For *unit* tests that only need a mocked session, use the ``session``
fixture (a MagicMock).  For *integration* tests that need a real database,
use ``db_session`` — each test gets a rolled-back transaction so nothing
persists.
"""

import os
import re

# --- Force test database BEFORE any app import ---
_PROD_URL = os.environ.get("PIVOT_DATABASE_URL", "")
if _PROD_URL:
    _TEST_DB_URL = re.sub(r"/([^/]+)$", r"/\1_test", _PROD_URL)
else:
    _TEST_DB_URL = "postgresql+psycopg://pivot:pivot@localhost:5432/pivot_test"
os.environ["PIVOT_DATABASE_URL"] = _TEST_DB_URL
os.environ.setdefault("PIVOT_DEBUG", "true")

from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.db import get_session
from app.main import app


# ---------- integration test fixtures ----------

_tables_created = False


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Real database session wrapped in a transaction that is rolled back.

    Tables are created lazily on first use, so unit-only runs never
    connect to postgres.
    """
    from sqlalchemy import Engine
    from sqlmodel import SQLModel, create_engine

    import app.models  # noqa: F401

    global _tables_created
    engine: Engine = create_engine(_TEST_DB_URL, echo=False)

    if not _tables_created:
        SQLModel.metadata.create_all(engine)
        _tables_created = True

    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def db_client(db_session: Session) -> Generator[TestClient, None, None]:
    """TestClient backed by a real (rolled-back) database session."""
    def _override() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_session] = _override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


# ---------- unit test fixtures (mocked session) ----------


@pytest.fixture(name="session")
def session_fixture() -> MagicMock:
    return MagicMock(spec=Session)


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    def _override() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_session] = _override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
