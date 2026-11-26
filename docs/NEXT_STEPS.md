# Next Steps

A checklist of the things you need to do yourself. The build order follows `IMPLEMENTATION_PLAN.md` §17. Tick items off as they're done.

_Last updated: 2026-11-25 (Steps 1–3 complete)_

## 1. Housekeeping (now)

- [ ] **Link the package-bundled agent skills.** Run this yourself from `backend/`: `uvx library-skills` (add `--claude` to also manage `.claude/skills`). It should find the `fastapi` and `typer` skills.
- [x] First commit made (`docker added`). `backend/uv.lock` is tracked; `.venv/` and `.env` are ignored.
- [x] Stray root `package-lock.json` is gone. The root `package.json` now only holds the Docker convenience scripts (no dependencies, no workspaces).
- [ ] **Optional: pin the Python version.** `pyproject.toml` requires `>=3.12` and the Docker image uses 3.12. Run `uv python pin 3.12` in `backend/` so native runs match.
- [ ] **Optional: unblock `pytest.exe`.** Windows Application Control blocks it on this machine. Use `python -m pytest` natively, or `npm test` (runs in Docker, unaffected).

## 2. Step 1: Repository Foundation (done)

- [x] Docker Desktop installed.
- [x] `docker-compose.yml` with `postgres`, `redis`, `backend`, `frontend` and a one-shot `migrate` (profile `db`, auto-enabled once `backend/alembic.ini` exists). `celery-worker` is added in the Celery step; `celery-beat` only once scheduling exists.
- [x] `docker/backend.Dockerfile` and `docker/frontend.Dockerfile`.
- [x] `.env.example`; `npm run up` creates `.env` automatically.
- [x] README quickstart (`npm run up` / `npm run down`); full command list in `CLAUDE.md`.
- [x] Verified: `npm run up:d` healthy, `/api/health` ok directly and through the Vite proxy, `npm test`, `npm run lint`, `npm run typecheck` pass in containers.

**Daily use:** `npm run up` starts everything; `npm run infra` starts only Postgres and Redis for native runs. If a local Postgres uses port 5432, set `POSTGRES_PORT` in `.env`.

## 3. Step 2: Database and Migrations (done)

- [x] `uv add alembic "psycopg[binary]"`.
- [x] `app/core/db.py` with lazy engine, `get_session` dependency, and `SessionDep` alias.
- [x] `app/core/config.py` now has `database_url` (PostgresDsn), `redis_url`, and `debug` settings.
- [x] `alembic init` done; `alembic/env.py` reads `PIVOT_DATABASE_URL` and uses `SQLModel.metadata`.
- [x] Initial empty baseline migration generated and applied.
- [x] `npm run up` auto-runs `alembic upgrade head` via the `migrate` service (activates when `alembic.ini` exists).
- [x] `/api/health` now returns `{"status":"ok","database":"ok"}` with a live DB check.
- [x] `app/models/` package created with `base.py` (shared field factories). Import new model files in `__init__.py`.
- [x] Tests use mock sessions natively; real Postgres runs in Docker via `npm run test:backend`.
- [x] Ruff per-file ignores for Alembic env/migration files; ruff post-write hook formats generated migrations.
- [ ] Dev seed mechanism (deferred to Step 3 when User/Workspace models exist).

**Note:** Windows Application Control blocks `alembic.exe` and `pytest.exe`. Use `uv run python -m pytest` natively, or `npm run test:backend` in Docker. Alembic commands are wrapped by `npm run db:*` scripts which run in Docker.

## 4. Step 3: Authentication and Workspaces (done)

Decisions settled: **JWT** auth, **workspace-role-only** permissions (owner/editor/viewer).

- [x] User model (`app/models/user.py`) with bcrypt password hashing.
- [x] Workspace and WorkspaceMembership models (`app/models/workspace.py`) with `WorkspaceRole` enum.
- [x] Auth utilities: `app/core/security.py` (password hashing, JWT creation/verification), `app/core/auth.py` (FastAPI dependencies: `CurrentUserDep`, `require_workspace_role`).
- [x] Auth API (`app/api/auth.py`): register, login, refresh, /me.
- [x] Workspace API (`app/api/workspaces.py`): CRUD + membership management (add/update/remove members).
- [x] Alembic migration for `user`, `workspace`, `workspacemembership` tables.
- [x] Auth settings in config: `PIVOT_SECRET_KEY`, `PIVOT_JWT_ALGORITHM`, `PIVOT_ACCESS_TOKEN_EXPIRE_MINUTES`, `PIVOT_REFRESH_TOKEN_EXPIRE_DAYS`.
- [x] 21 tests (11 auth, 2 health, 8 workspace/permissions). All pass natively and in Docker.
- [x] End-to-end verified: register → login → /me → create workspace → list workspaces → 401 on no-token.
- [ ] Dev seed script (create a default user + workspace for local dev).
- [ ] `PIVOT_SECRET_KEY` must be changed in production (default is a placeholder).

## 5. Step 4: Workflow Storage (next)

Requires settling one decision from §20 first:
- **Workflow graph storage:** JSON-only / normalized tables / hybrid

Deliverables:
- [ ] Workflow Pydantic models (definition schema with `schema_version`, `nodes[]`, `edges[]`)
- [ ] SQLModel Workflow table
- [ ] CRUD API: list, create, read, update, archive, duplicate, import, export
- [ ] Workflow schema validation (reject cycles, validate node types)
- [ ] Frontend workflow service (`src/services/`)
- [ ] Migration and tests

## 6. Decisions you need to make (plan §20)

Settle each one before its step starts:

| Decision | Needed before | Options | Status |
|---|---|---|---|
| Authentication strategy | Step 3 | JWT / cookie sessions / external IdP | ✅ JWT |
| Permission model | Step 3 | Workspace role only / per-workflow / both | ✅ Workspace role only |
| Workflow graph storage | Step 4 (workflow storage) | JSON-only / normalized nodes and edges tables / hybrid | **decide next** |
| Execution data storage | Step 6 (execution persistence) | Postgres only / plus Redis cache / plus object storage for large outputs | |
| First HTTP node behavior | Step 5 (node registry) | Basic request/response / headers and auth / credentials and secret references | |
| Frontend editor scope | Step 8 (editor) | Full palette / small first palette / schema-generated forms | |
| Real-time monitoring | Step 9 (monitoring UI) | Polling first (the plan's default) / WebSockets from the start | |
| Frontend package manager | Any time | npm (current) / pnpm | |

## 7. Later steps (for reference)

Step 4 workflow storage, Step 5 node registry, Step 6 execution persistence, Step 7 Celery workers, Step 8 Vue Flow editor, Step 9 monitoring UI and Step 10 the vertical-slice test. Docs and CI hardening follow.
