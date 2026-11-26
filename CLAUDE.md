# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

Pivot is a visual, node-based workflow automation platform (Vue 3 + FastAPI + Celery). `IMPLEMENTATION_PLAN.md` is the authoritative spec for the first milestone. Currently only a minimal skeleton exists: a FastAPI app exposing `GET /api/health`, and a Vue 3 + TS (Vite) app that calls it. Docker Compose runs the dev stack (Postgres, Redis, backend, frontend). SQLModel + Alembic are set up with auto-migrations. JWT authentication, User, Workspace, and WorkspaceMembership models are in place with role-based access control (owner/editor/viewer). There is no Celery or workflow storage yet (next: Step 4, workflow storage; see `docs/NEXT_STEPS.md`). Package management is npm (frontend) and uv (backend, `pyproject.toml` + `uv.lock`).

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

Authentication: JWT-based (`app/core/security.py` for token creation/verification and password hashing, `app/core/auth.py` for FastAPI dependencies). Protected routes use `CurrentUserDep` (extracts user from Bearer token). Workspace-scoped routes call `require_workspace_role(session, workspace_id, user, minimum_role)` to enforce RBAC. Auth routes are at `/api/auth/` (register, login, refresh, me); workspace routes at `/api/workspaces/`. Settings: `PIVOT_SECRET_KEY`, `PIVOT_JWT_ALGORITHM`, `PIVOT_ACCESS_TOKEN_EXPIRE_MINUTES`, `PIVOT_REFRESH_TOKEN_EXPIRE_DAYS`.

The frontend calls the backend only through relative `/api/...` URLs in `src/services/`. API functions take an injectable `fetchFn` so they can be unit-tested without a server.

Before implementing anything, read the relevant section of `IMPLEMENTATION_PLAN.md` and check `docs/NEXT_STEPS.md`, the user-facing checklist. Update it when a step or decision is completed. Work proceeds in the order given in its §17 "Implementation Sequence" (repo foundation → DB/migrations → auth/workspaces → workflow storage → node registry → execution persistence → Celery → editor → monitoring UI → vertical-slice test). Section §20 lists open decisions (auth strategy, package managers, graph storage, permission granularity, polling vs. WebSockets). Ask the user to settle the relevant one before starting the step it affects; don't pick silently.

**First milestone target:** a signed-in user creates a workflow in the editor (manual trigger → HTTP request → transform → condition), saves it, runs it asynchronously, and views execution status and per-node output.

## Planned stack and layout

- `frontend/`: Vue 3, TypeScript, Vue Flow (editor), Vitest. Feature folders under `src/features/` (auth, workspaces, workflows, editor, executions).
- `backend/`: Python, FastAPI, SQLModel (ORM, preferred over raw SQLAlchemy per the FastAPI skill), Alembic, Pydantic, Celery, Pytest. Routes live under `/api/` (auth, workspaces, workflows, executions, nodes, users), with no version segment.
- Infrastructure: PostgreSQL (all durable state), Redis (Celery broker), and Docker Compose for local dev, with services `frontend`, `backend`, `postgres`, `redis`, and `celery-worker`. Add `celery-beat` only once scheduling exists.
- Also planned: `docker/`, `docs/`, `.github/workflows/`.

## Architectural invariants

These come from the plan and span multiple components. Preserve them:

- **Workflow definition is versioned JSON** (`schema_version`, `nodes[]` with stable `id`/`type`/`position`/`config`, `edges[]` with `source`/`target` and optional condition). JSON stays the canonical import/export format even if graph tables are added later.
- **Node registry, not engine special-cases.** Each node type provides: a Pydantic config model, Pydantic input/output models, an executor, registry registration, and frontend metadata. The editor's node palette comes from the backend registry (`/api/nodes`). Adding a node must never require changes to dependency resolution or orchestration. Initial nodes: `manual_trigger`, `http_request`, `transform`, `condition`.
- **Execution flow:** the API validates the graph and rejects cycles, creates a `WorkflowExecution` row in `queued` status *before* enqueuing, enqueues a Celery task, and returns the execution ID immediately. The worker resolves the topological order, runs ready nodes, propagates outputs along edges, evaluates condition branches, and persists a `NodeExecution` row per node. Execution state must live in PostgreSQL, never only in worker memory.
- Execution statuses: `queued`, `running`, `succeeded`, `failed`, `cancelled`. Node failure behaviors: `stop`, `continue`, `retry`.
- **Monitoring:** the frontend polls REST endpoints first. WebSockets come later as a notification layer only; REST/Postgres remains the source of truth.
- **Tenancy:** every workflow belongs to a `Workspace`. Membership roles are `owner`, `editor`, and `viewer`: editors edit and execute, viewers read, and only owners manage membership. Enforce this on every workflow and execution route on the backend; frontend checks are cosmetic.

## Security requirements baked into the design

- Never log secrets or return them in API responses or workflow exports. Redact auth headers in logs.
- HTTP node: validate URLs and allowed protocols, block private, loopback, and link-local addresses (SSRF) unless an explicit safe mode is set, restrict redirects, cap response size, and enforce timeouts.
- JWT auth uses short-lived access tokens (30 min) and longer refresh tokens (7 days). `PIVOT_SECRET_KEY` must be changed in production. Use a CORS allowlist.

## Testing expectations

Tests are part of each step, not a later cleanup. The HTTP node tests must mock external requests and never hit the public internet. The end-to-end acceptance test is the vertical slice in `IMPLEMENTATION_PLAN.md` §14.3.
