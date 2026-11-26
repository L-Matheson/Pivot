"""Permission checking utilities for role-based access control."""

from typing import Any

from app.models.role import Role


def check_permission(
    role: Role,
    resource: str,
    action: str,
    scope: str | None = None,
) -> bool:
    if role.full_access:
        return True

    perms: dict[str, Any] = role.permissions or {}
    resource_perms = perms.get(resource)
    if resource_perms is None:
        return False

    action_value = resource_perms.get(action)
    if action_value is True:
        return True
    if action_value is False or action_value is None:
        return False
    if isinstance(action_value, list):
        if "*" in action_value:
            return True
        if scope is not None and scope in action_value:
            return True

    return False
