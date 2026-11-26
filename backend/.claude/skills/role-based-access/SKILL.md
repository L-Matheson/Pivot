---
name: role-based-access
description: Implement permission-based access control with dynamic roles. Roles use full_access flag for bypass, not hardcoded IDs or names. Routes declare permissions via FastAPI dependencies.
allowed-tools: Read, Write, Edit, Glob
---

You implement permission-based RBAC for Pivot where any role — system or custom — can grant any combination of permissions.

## Core Principles

1. **No hardcoded role IDs or names.** Roles are identified by their UUID primary key. The admin bypass is `role.full_access`, a boolean column — not a UUID comparison or name string match.
2. **Routes declare permissions via dependencies, not function calls.** `dependencies=[Depends(PermissionRequired("members", "manage"))]` on the route decorator — not `require_admin()` or `require_permission()` at the top of the function body.
3. **Custom roles are first-class.** A custom "Team Lead" role with `"members": {"manage": true}` can manage members identically to the system admin.
4. **Owner protection uses `workspace.owner_user_id`.** Multiple users can share the admin role; only the workspace owner is immutable.
5. **Role names are unique per workspace** via DB constraint `UNIQUE(workspace_id, name)`.

## Permission Structure

Permissions are JSONB on the Role model:

```json
{
  "resource": {
    "action": true | false | ["scope:value", ...]
  }
}
```

**Resources and actions:**

| Resource | Actions | Notes |
|---|---|---|
| `automations` | `view`, `edit`, `execute`, `manage` | Scoped: `["folder:finance", "tag:hr"]` or `["*"]` |
| `connections` | `view`, `manage` | |
| `members` | `view`, `manage` | |
| `roles` | `view`, `manage` | |
| `settings` | `view`, `manage` | Workspace settings, theme |
| `stats` | `view` | |

**Action values:**
- `true` — granted globally
- `false` — denied
- `["*"]` — granted for all scopes
- `["folder:finance", "tag:ops"]` — granted only for listed scopes

## System Roles

Two system roles are seeded by migration. They have `is_system=True` and normal UUID4 primary keys.

- **System admin**: `full_access=True`, empty `permissions`. The `full_access` flag causes `check_permission` to return `True` for everything.
- **System member**: `full_access=False`. Read-only baseline via JSONB permissions.

System roles cannot be modified or deleted through the API.

## Implementation

### Role Model (app/models/role.py)

```python
class Role(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("workspace_id", "name", name="uq_role_workspace_name"),
    )
    id: uuid.UUID = id_field()
    workspace_id: uuid.UUID | None = Field(default=None, ...)
    name: str = Field(max_length=100)
    is_system: bool = Field(default=False)
    full_access: bool = Field(default=False)
    permissions: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB, ...))
```

### Permission Check (app/core/permissions.py)

```python
def check_permission(role, resource, action, scope=None) -> bool:
    if role.full_access:
        return True
    perms = role.permissions or {}
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
```

### Auth Dependencies (app/core/auth.py)

```python
class WorkspaceMemberRequired:
    """Validates workspace membership. Use as Depends()."""
    def __call__(self, workspace_id, session, user):
        membership = _get_membership(session, workspace_id, user.id)
        if membership is None:
            raise HTTPException(404, "Workspace not found.")
        role = _get_member_role(session, membership)
        return membership, role

class PermissionRequired:
    """Validates a specific permission. Use as Depends()."""
    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action

    def __call__(self, workspace_id, session, user):
        membership = _get_membership(session, workspace_id, user.id)
        if membership is None:
            raise HTTPException(404, "Workspace not found.")
        role = _get_member_role(session, membership)
        if not check_permission(role, self.resource, self.action):
            raise HTTPException(403, f"Missing permission: {self.resource}.{self.action}")
        return membership, role

WorkspaceMemberDep = Annotated[tuple[WorkspaceMembership, Role], Depends(WorkspaceMemberRequired())]
```

### Applying to Routes

Permission declared on the route decorator:

```python
@router.patch(
    "/{workspace_id}",
    dependencies=[Depends(PermissionRequired("settings", "manage"))],
)
def update_workspace(workspace_id, body, session):
    ...

@router.get("/{workspace_id}")
def get_workspace(workspace_id, _auth: WorkspaceMemberDep, session):
    ...
```

### File Structure

Each resource has its own route file:

- `app/api/workspaces.py` — workspace CRUD
- `app/api/members.py` — member management (`/workspaces/{workspace_id}/members`)
- `app/api/roles.py` — role CRUD (`/workspaces/{workspace_id}/roles`)

### Owner Protection

```python
workspace = session.get(Workspace, workspace_id)
if workspace.owner_user_id == member_id:
    raise HTTPException(422, "Cannot change the workspace owner's role.")
```

## Anti-Patterns

- `role.name == "admin"` — names are labels, not identity
- `role.id == UUID("00000000-...")` — hardcoded UUIDs couple code to migration seeds
- `require_admin(session, workspace_id, user)` at the top of a function — use `dependencies=[Depends(PermissionRequired(...))]`
- `require_role("admin", "lead")` decorator — cannot handle dynamic roles
- `is_admin(role)` for member protection — use `workspace.owner_user_id`
