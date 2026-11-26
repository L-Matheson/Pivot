"""Shared test fixtures."""

import os

os.environ.setdefault("PIVOT_DEBUG", "true")

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.db import get_session
from app.main import app


@pytest.fixture(name="session")
def session_fixture() -> MagicMock:
    return MagicMock(spec=Session)


@pytest.fixture(name="client")
def client_fixture(session: Session) -> TestClient:
    def _override():  # type: ignore[no-untyped-def]
        yield session

    app.dependency_overrides[get_session] = _override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
