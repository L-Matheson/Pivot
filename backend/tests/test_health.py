"""Health endpoint tests."""

from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"


def test_health_reports_database_status(client: TestClient) -> None:
    """The response includes a database field."""
    data = client.get("/api/health").json()
    assert "database" in data
