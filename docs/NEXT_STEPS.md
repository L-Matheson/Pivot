# Next Steps

A checklist of the things you need to do yourself. The build order follows `IMPLEMENTATION_PLAN.md` §17. Tick items off as they're done.

_Last updated: 2026-11-25 (Steps 1–2 complete)_

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

## 4. Step 3: Authentication and Workspaces (next)

Requires settling two decisions from §20 first:
- **Authentication strategy:** Secure cookie sessions (needs CSRF) / JWT / external identity provider
- **Permission model:** Workspace role only / per-workflow / both

Deliverables:
- [ ] User model and registration
- [ ] Login/logout endpoints
- [ ] Current-user endpoint
- [ ] Workspace creation and membership models
- [ ] Role enforcement (owner / editor / viewer)
- [ ] Migration for all new tables
- [ ] Tests for auth and permission boundaries

## 5. Decisions you need to make (plan §20)

Settle each one before its step starts:

| Decision | Needed before | Options |
|---|---|---|
| Authentication strategy | Step 3 (auth/workspaces) | Secure cookie sessions (needs CSRF) / JWT / external identity provider |
| Permission model | Step 3 | Workspace role only / per-workflow / both |
| Workflow graph storage | Step 4 (workflow storage) | JSON-only / normalized nodes and edges tables / hybrid |
| Execution data storage | Step 6 (execution persistence) | Postgres only / plus Redis cache / plus object storage for large outputs |
| First HTTP node behavior | Step 5 (node registry) | Basic request/response / headers and auth / credentials and secret references |
| Frontend editor scope | Step 8 (editor) | Full palette / small first palette / schema-generated forms |
| Real-time monitoring | Step 9 (monitoring UI) | Polling first (the plan's default) / WebSockets from the start |
| Frontend package manager | Any time | npm (current) / pnpm |

## 6. Later steps (for reference)

Step 3 auth and workspaces, then Step 4 workflow storage, Step 5 node registry, Step 6 execution persistence, Step 7 Celery workers, Step 8 Vue Flow editor, Step 9 monitoring UI and Step 10 the vertical-slice test. Docs and CI hardening follow.
