"""Single source of truth for permission resources and actions.

Every PermissionRequired() call in the API layer uses resource/action
strings defined here. The frontend role editor reads the same list via
GET /api/permissions.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class PermissionAction:
    slug: str
    label: str


@dataclass(frozen=True, slots=True)
class PermissionResource:
    slug: str
    label: str
    actions: tuple[PermissionAction, ...]


VIEW = PermissionAction("view", "View")
CREATE = PermissionAction("create", "Create")
EDIT = PermissionAction("edit", "Edit")
DELETE = PermissionAction("delete", "Delete")
MANAGE = PermissionAction("manage", "Manage")

PERMISSION_RESOURCES: tuple[PermissionResource, ...] = (
    PermissionResource("automations", "Automations", (VIEW, CREATE, EDIT, DELETE, MANAGE)),
    PermissionResource("connections", "Connections", (VIEW, MANAGE)),
    PermissionResource("members", "Members", (VIEW, MANAGE)),
    PermissionResource("roles", "Roles", (VIEW, MANAGE)),
    PermissionResource("settings", "Settings", (VIEW, MANAGE)),
    PermissionResource("stats", "Stats", (VIEW,)),
)

_VALID_PAIRS: frozenset[tuple[str, str]] = frozenset(
    (r.slug, a.slug) for r in PERMISSION_RESOURCES for a in r.actions
)


def is_valid_permission(resource: str, action: str) -> bool:
    return (resource, action) in _VALID_PAIRS


def all_resource_slugs() -> list[str]:
    return [r.slug for r in PERMISSION_RESOURCES]


def actions_for_resource(resource: str) -> list[str]:
    for r in PERMISSION_RESOURCES:
        if r.slug == resource:
            return [a.slug for a in r.actions]
    return []


def serialize() -> list[dict]:
    return [
        {
            "slug": r.slug,
            "label": r.label,
            "actions": [{"slug": a.slug, "label": a.label} for a in r.actions],
        }
        for r in PERMISSION_RESOURCES
    ]
