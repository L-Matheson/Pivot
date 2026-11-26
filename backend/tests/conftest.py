"""Shared test fixtures.

Unit tests use a mock session so they run anywhere (no database driver needed).
Integration tests that need real Postgres run via ``npm run test:backend``
inside the Docker backend container, where the driver is available.
"""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.db import get_session
from app.main import app


@pytest.fixture(name="session")
def session_fixture() -> MagicMock:
    """A mock database session for unit tests.

    Returns a MagicMock with the Session spec.  Calls like
    ``session.exec(text("SELECT 1"))`` succeed without a live database,
    which is enough for endpoint-level tests that only check response shape.
    """
    return MagicMock(spec=Session)


@pytest.fixture(name="client")
def client_fixture(session: Session) -> TestClient:
    """TestClient with the database session overridden by the mock."""

    def _override():  # type: ignore[no-untyped-def]
        yield session

    app.dependency_overrides[get_session] = _override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
