# Next Steps

Checklist tracking implementation progress. Build order follows `IMPLEMENTATION_PLAN.md`. Tick items as they're done.

_Last updated: 2026-11-27 (Steps 1–5 complete, workflow storage + editor integration)_

---

## Phase 1: Core Platform

### Step 1: Repository Foundation (done)

- [x] Docker Compose with postgres, redis, backend, frontend, migrate services
- [x] Dockerfiles, .env.example, npm convenience scripts
- [x] Verified: health endpoint, Vite proxy, tests pass in containers

### Step 2: Database and Migrations (done)

- [x] SQLModel + Alembic set up with auto-migrations
- [x] Lazy engine, get_session dependency, SessionDep alias
- [x] Base model field factories (id_field, created_at_field, updated_at_field)
- [x] Health endpoint with live DB check

### Step 3: Authentication and Workspaces (done)

- [x] User model with bcrypt password hashing
- [x] Workspace and WorkspaceMembership models (owner/editor/viewer)
- [x] JWT auth with issuer/audience validation, production secret enforcement
- [x] Auth API (register, login, refresh, logout, /me)
- [x] Workspace CRUD + membership management
- [x] Swagger docs disabled in production
- [x] 21 backend tests, 6 frontend tests — all passing

### Step 4: Custom Roles and Permissions (done)

- [x] Role model with `full_access` flag (no hardcoded UUIDs or name-based identity)
- [x] System roles seeded via migration (admin: `full_access=True`, member: restricted JSONB)
- [x] Permission-based auth via FastAPI dependency classes (`PermissionRequired`, `WorkspaceMemberRequired`)
- [x] Routes declare permissions on the decorator, not in function body
- [x] Custom role CRUD API (workspace-scoped, permission-gated): list, create, get, update, delete
- [x] Permission checking: `full_access` bypass, resource/action/scope resolution from JSONB
- [x] Dynamic roles: any role with the right permission can perform the action (not role-name-locked)
- [x] Owner protection via `workspace.owner_user_id` (not role checks)
- [x] WorkspaceMembership migrated from role enum to role_id FK
- [x] Unique constraint on `(workspace_id, name)` for role names
- [x] Split routes: workspaces.py, members.py, roles.py
- [x] 38 backend tests passing
- [x] Folder and tag fields on workflows for permission scoping

### Step 5: Workflow Storage (done)

- [x] Workflow Pydantic models (definition schema: schema_version, nodes, edges, with nested validation)
- [x] SQLModel Workflow table (workspace_id, name, description, folder, tags JSONB, definition JSONB, is_active, is_archived, created_by)
- [x] CRUD API: list (permission-filtered), create, read, update, archive, duplicate, delete
- [x] Workflow schema validation (cycle detection via DFS, orphan edge detection, duplicate node ID check)
- [x] Graph validation utilities (app/core/graph.py)
- [x] Migration and 14 backend tests
- [x] Frontend: node type slug mapping (nodeTypes.ts), API service, TanStack Query composable
- [x] Frontend: create-first flow (dialog → API create → editor with real ID, workflow persists if user leaves)
- [x] Frontend: editor loads/saves workflow definition to backend (VueFlow ↔ backend format conversion)
- [x] Frontend: node config panel (per-type fields, connection warnings for nodes requiring a connected account)
- [x] Frontend: node selection highlight (ring on selected node)
- [ ] Import/export endpoints (deferred — JSON export/import of workflow definitions)

### Step 6: Connection Infrastructure

- [ ] Connection model (workspace_id, provider, auth_type, credentials_encrypted)
- [ ] PIVOT_ENCRYPTION_KEY setting and encryption utilities
- [ ] Connector registry (provider definitions with auth config)
- [ ] Connection CRUD API (create, list, test, delete — credentials never returned)
- [ ] OAuth2 flow: authorize URL endpoint, callback handler, token refresh
- [ ] API key and connection string storage (encrypted)
- [ ] Google OAuth connector (Gmail + Sheets) — first provider
- [ ] Migration and tests

---

## Phase 2: Execution Engine

### Step 7: Node Registry and Engine

- [ ] Node registry with Pydantic config/input/output models per type
- [ ] Node metadata API (`/api/nodes`)
- [ ] Node executors: manual_trigger, email_trigger, http_request, send_email, write_spreadsheet, send_notification, transform, condition
- [ ] Topological dependency resolution and cycle detection
- [ ] Branching execution (if/else, parallel)
- [ ] Data propagation between nodes
- [ ] Tests (mocked external calls)

### Step 8: Execution Persistence

- [ ] WorkflowExecution and NodeExecution models
- [ ] Execution CRUD API (create, list, detail — permission-filtered)
- [ ] Status management (queued → running → succeeded/failed)
- [ ] Node-level input/output/error storage
- [ ] Retry and cancellation
- [ ] Migration and tests

### Step 9: Celery Workers and Triggers

- [ ] Celery app config with Redis broker
- [ ] Workflow execution Celery task
- [ ] celery-worker Docker service
- [ ] celery-beat for scheduled/polling triggers
- [ ] Email trigger (poll Gmail for labeled messages)
- [ ] Schedule trigger (cron expressions)
- [ ] API poll trigger (website/endpoint monitoring with change detection)
- [ ] Tests

---

## Phase 3: Frontend

### Step 10: Theming Infrastructure

- [x] CSS custom property system (all colors from variables)
- [x] Theme provider composable (reads workspace theme_config, uses VueUse useDark)
- [x] Light and dark mode (VueUse useDark, persisted to localStorage)
- [ ] Theme settings API (admin-only)
- [x] Color picker in workspace settings

### Step 11: Auth and Workspace UI

- [x] Login and registration pages
- [x] Workspace selector
- [x] Workspace settings (name, theme, danger zone)
- [ ] Member management (invite, assign roles)
- [ ] Custom role editor
- [x] Vue Router with auth guards, Pinia stores

### Step 12: Visual Workflow Editor

- [ ] Workflow list page (filtered by permissions)
- [ ] Editor canvas (Vue Flow) with pan/zoom
- [ ] Node palette sidebar (from backend registry)
- [ ] Drag-and-drop, edge creation/deletion
- [ ] Node config forms (auto-generated from schema)
- [ ] Connection selector in node config
- [ ] Branching visualization
- [ ] Save/load, unsaved-change indicator

### Step 13: Execution Monitoring UI

- [ ] Run workflow action
- [ ] Execution list and detail pages
- [ ] Node status display and input/output inspector
- [ ] Error display, polling for updates

---

## Phase 4: Dashboards and Polish

### Step 14: Stats Dashboards

- [ ] Workflow stats (execution counts, success rates, durations)
- [ ] Execution analytics (trends, failure categories)
- [ ] Admin platform stats (connections, users, storage)
- [ ] Audit log viewer

### Step 15: Connections UI

- [ ] Connections page (list, status indicators)
- [ ] OAuth connect flow (Google, Slack, Microsoft)
- [ ] API key and connection string forms
- [ ] Connection test and usage display

### Step 16: Documentation and CI/CD

- [ ] Setup guide, env var reference
- [ ] Connector and node development guides
- [ ] GitHub Actions CI
- [ ] Production deployment guide

---

## Decisions

| Decision | Status | Choice |
|---|---|---|
| Authentication | ✅ | In-memory access token (15 min) + httpOnly cookie refresh token (30 days) |
| Permission model | ✅ | System roles (admin/member) + custom roles, folder/tag scoping |
| Deployment model | ✅ | Multi-tenant SaaS |
| Integration auth | ✅ | OAuth first, API keys as fallback |
| First vertical slice | ✅ | Email trigger → notification + spreadsheet write |
| Target user | ✅ | Non-technical business users |
| Branching | ✅ | If/else and parallel from the start |
| Billing | Deferred | Build product first |
| Graph storage | ✅ | JSON-only (JSONB column) |
| Execution storage | ✅ | PostgreSQL only initially |
| Real-time | ✅ | Polling first, WebSockets later |
| Package managers | ✅ | npm (frontend), uv (backend) |
