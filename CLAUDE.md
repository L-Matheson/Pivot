# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

Pivot is a multi-tenant SaaS business automation platform (Vue 3 + FastAPI + Celery). Organizations connect their systems (email, databases, APIs, spreadsheets, messaging) and build visual workflows that trigger and act automatically. The target user is non-technical — a drag-and-drop visual builder, no code.

`IMPLEMENTATION_PLAN.md` is the authoritative spec. Currently: FastAPI backend with JWT auth, User/Workspace/WorkspaceMembership models with RBAC (owner/editor/viewer), PostgreSQL via SQLModel + Alembic with auto-migrations, Vue 3 + TS frontend (Vite), Docker Compose dev stack. No Celery, workflow storage, or connections yet.

**Next step:** Step 4 — Custom roles and permissions (extend workspace roles to support custom roles with JSONB permissions, folder/tag-based automation scoping). See `docs/NEXT_STEPS.md`.

**First milestone target:** a signed-in user connects a Gmail account, creates a workflow that triggers on a labeled email, sends a notification, and writes to a Google Sheet — all through the visual editor.

## Commands

**Whole stack (preferred), run from the repo root.** Needs Docker; `.env` is auto-created from `.env.example`.

```sh
npm run up           # build + start postgres, redis, backend (:8000), frontend (:5173) with hot reload
npm run up:d         # same, detached and waits until healthy
npm run down         # stop (data kept); npm run reset also wipes volumes
npm run logs | ps | restart
npm run infra        # only postgres + redis, to run backend/frontend natively as below
npm test             # backend pytest + frontend vitest in containers; also lint, format, typecheck
npm run db:revision -- "message"   # autogenerate Alembic migration; db:migrate, db:downgrade, db:current, db:check, db:psql, db:reset
```

`npm run up` applies migrations automatically via the one-shot `migrate` service, which activates once `backend/alembic.ini` exists. If a local Postgres already owns port 5432, set `POSTGRES_PORT` in `.env`.

Running natively instead:

Backend (run from `backend/`, managed with uv; add deps with `uv add <pkg>` / `uv add --dev <pkg>`, never hand-edit `uv.lock`):

```sh
uv sync                                                     # create .venv and install deps
uv run fastapi dev                                          # serves on :8000 (entrypoint in [tool.fastapi])
uv run python -m pytest                                     # all tests
uv run python -m pytest tests/test_health.py::test_health_returns_ok   # single test
uv run ruff check . && uv run ruff format --check .
```

Use `python -m pytest`, not `uv run pytest`: Windows Application Control blocks the `pytest.exe` launcher on this machine.

FastAPI ships an agent skill at `backend/.venv/Lib/site-packages/fastapi/.agents/skills/fastapi/SKILL.md` (and `references/`). Read it before writing backend code and follow its conventions: `Annotated` parameters and dependencies, return types instead of `response_model` where possible, prefix and tags declared on the `APIRouter` itself, sync `def` unless the code is fully async-safe, and no `RootModel` or `...` defaults.

Frontend (run from `frontend/`):

```sh
npm install
npm run dev          # :5173, proxies /api -> http://localhost:8000 (override with VITE_API_PROXY_TARGET)
npm test             # vitest run; single file: npx vitest run src/services/api.test.ts
npm run typecheck    # vue-tsc
npm run build
```

## Backend structure

`app/main.py` builds the app with `create_app()`. Each resource gets one module in `app/api/` (e.g. `app/api/health.py`) that declares its own `APIRouter(prefix="/<resource>", tags=[...])`. `app/api/__init__.py` mounts them all under `/api`. Register a new module there. The URL has no version segment, because API versioning is handled through git and GitHub releases, not URL paths or folders. Settings live in `app/core/config.py` (pydantic-settings). Env vars use the `PIVOT_` prefix and can also come from `backend/.env`, e.g. `PIVOT_CORS_ORIGINS='["http://localhost:5173"]'`.

Database: `app/core/db.py` provides a lazy engine (created on first use, not at import time), a `get_session` dependency, and a `SessionDep` type alias. Table models go in `app/models/` as SQLModel `table=True` classes; each new model file must be imported in `app/models/__init__.py` so Alembic sees it. Shared field factories (`id_field`, `created_at_field`, `updated_at_field`) live in `app/models/base.py`. Alembic config is in `backend/alembic.ini`; `alembic/env.py` reads `PIVOT_DATABASE_URL` from settings. Migrations in `alembic/versions/` are auto-generated and auto-applied by `npm run up`.

Authentication: JWT-based (`app/core/security.py` for token creation/verification and password hashing, `app/core/auth.py` for FastAPI dependencies). Protected routes use `CurrentUserDep` (extracts user from Bearer token). Workspace-scoped routes call `require_workspace_role(session, workspace_id, user, minimum_role)` to enforce RBAC. Auth routes are at `/api/auth/` (register, login, refresh, me); workspace routes at `/api/workspaces/`. Settings: `PIVOT_SECRET_KEY`, `PIVOT_JWT_ALGORITHM`, `PIVOT_JWT_ISSUER`, `PIVOT_JWT_AUDIENCE`, `PIVOT_ACCESS_TOKEN_EXPIRE_MINUTES`, `PIVOT_REFRESH_TOKEN_EXPIRE_DAYS`. Swagger docs are disabled when `PIVOT_DEBUG=false`.

The frontend calls the backend only through relative `/api/...` URLs in `src/services/`. API functions take an injectable `fetchFn` so they can be unit-tested without a server.

Before implementing anything, read the relevant section of `IMPLEMENTATION_PLAN.md` and check `docs/NEXT_STEPS.md`, the user-facing checklist. Update it when a step or decision is completed.

## Planned stack and layout

- `frontend/`: Vue 3, TypeScript, Vue Flow (editor), Pinia (state), Vue Router, Vitest. Feature folders under `src/features/`.
- `backend/`: Python, FastAPI, SQLModel, Alembic, Pydantic, Celery, Pytest. Routes under `/api/`, no version segment.
- Infrastructure: PostgreSQL (all durable state), Redis (Celery broker + cache), Docker Compose for local dev with services `frontend`, `backend`, `postgres`, `redis`, `celery-worker`. Add `celery-beat` once scheduling exists.

## Architectural invariants

- **Multi-tenant isolation.** Every query is scoped to the authenticated user's workspace. No cross-workspace data access through the API. Background workers validate workspace context before executing.
- **Workflow definition is versioned JSON** (`schema_version`, `nodes[]` with stable `id`/`type`/`position`/`config`, `edges[]` with `source`/`target` and optional condition). JSON stays the canonical import/export format.
- **Node registry, not engine special-cases.** Each node type provides: a Pydantic config model, Pydantic input/output models, an executor, registry registration, and frontend metadata. Adding a node must never require changes to dependency resolution or orchestration.
- **Execution flow:** the API validates the graph and rejects cycles, creates a `WorkflowExecution` row in `queued` status *before* enqueuing, enqueues a Celery task, and returns the execution ID immediately. The worker resolves topological order, runs ready nodes, propagates outputs, evaluates branches, and persists a `NodeExecution` row per node. Execution state lives in PostgreSQL, never only in worker memory.
- **Connections are encrypted.** OAuth tokens, API keys, and connection strings are encrypted at rest using `PIVOT_ENCRYPTION_KEY`. Credentials are never logged or returned in API responses.
- **Permissions are backend-enforced.** Custom roles with JSONB permissions control visibility at the folder/tag level. Frontend permission checks are cosmetic only.
- **Theming is fully dynamic.** All frontend colors derive from CSS custom properties loaded from workspace theme_config. No hardcoded brand colors.

## Security requirements

- Never log secrets or return them in API responses or workflow exports. Redact auth headers in logs.
- HTTP/API poll nodes: validate URLs, block private/loopback/link-local addresses (SSRF), restrict redirects, cap response size, enforce timeouts.
- JWT auth uses short-lived access tokens (30 min) and longer refresh tokens (7 days). `PIVOT_SECRET_KEY` is rejected if default when `PIVOT_DEBUG=false`. Tokens include issuer/audience claims.
- Encrypted credential store for all connection secrets (OAuth tokens, API keys, connection strings).
- CORS allowlist. Rate limiting. Input validation. Swagger docs disabled in production.

## Testing expectations

Tests are part of each step, not a later cleanup. Node executor tests must mock external calls and never hit the public internet. Integration tests prove the vertical slice end-to-end.
