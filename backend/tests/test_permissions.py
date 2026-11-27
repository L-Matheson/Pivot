"""Permission catalog endpoint tests."""

from fastapi.testclient import TestClient


def test_list_permissions_returns_all_resources(client: TestClient) -> None:
    response = client.get("/api/permissions")
    assert response.status_code == 200
    data = response.json()
    slugs = [r["slug"] for r in data]
    assert "automations" in slugs
    assert "connections" in slugs
    assert "members" in slugs
    assert "roles" in slugs
    assert "settings" in slugs
    assert "stats" in slugs


def test_each_resource_has_actions(client: TestClient) -> None:
    data = client.get("/api/permissions").json()
    for resource in data:
        assert "slug" in resource
        assert "label" in resource
        assert "actions" in resource
        assert len(resource["actions"]) > 0
        for action in resource["actions"]:
            assert "slug" in action
            assert "label" in action
