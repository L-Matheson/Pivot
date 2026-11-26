# Next Steps

A checklist of the things you need to do yourself. The build order follows `IMPLEMENTATION_PLAN.md` §17. Tick items off as they're done.

_Last updated: 2026-11-25_

## 1. Housekeeping (now)

- [ ] **Link the package-bundled agent skills.** The automated run was blocked by permissions, so run this yourself from `backend/`:
      `uvx library-skills` (add `--claude` to also manage `.claude/skills`). It should find the `fastapi` and `typer` skills.
- [ ] **Make the first commit.** Everything (`backend/`, `frontend/`, `docs/`, `.agents/`, `CLAUDE.md`, `IMPLEMENTATION_PLAN.md`) is still untracked on `main`.
      Commit `backend/uv.lock`. Never commit `.venv/` or `.env`, which `.gitignore` already excludes.
- [ ] **Delete the stray root `package-lock.json`.** It's empty because there's no root `package.json`. Keep it only if you plan npm workspaces.
- [ ] **Optional: pin the Python version.** uv built the venv on Python 3.15.2, but `pyproject.toml` only requires `>=3.12`.
      Run `uv python pin 3.12` (or 3.13) in `backend/` if you want the version to match the planned Docker image.
- [ ] **Optional: unblock `pytest.exe`.** Windows Application Control blocks it. Allow it, or keep using `uv run python -m pytest`.

## 2. Finish Step 1: Repository Foundation

These deliverables are still missing:

- [ ] Install **Docker Desktop**, which Docker Compose needs.
- [ ] Write `docker-compose.yml` with services `frontend`, `backend`, `postgres`, `redis` and `celery-worker`. Add `celery-beat` later.
- [ ] Add a `backend/Dockerfile` (uv-based) and a `frontend/Dockerfile`.
- [ ] Add a `.env.example` listing every `PIVOT_*` variable, including the future `PIVOT_DATABASE_URL` and `PIVOT_REDIS_URL`.
- [ ] Add README setup instructions: `uv sync`, `npm install`, `docker compose up`.

Acceptance: Postgres and Redis start, `GET /api/health` returns ok, the frontend loads, and everything runs in Docker.

## 3. Step 2: Database and Migrations (SQLModel + Alembic)

`sqlmodel` is already a backend dependency.

- [ ] `uv add alembic "psycopg[binary]"` (the Postgres driver).
- [ ] Add `app/core/db.py` with the engine, a `get_session` dependency and a `SessionDep = Annotated[Session, Depends(get_session)]` alias (FastAPI-skill style).
- [ ] Run `alembic init`, point `target_metadata` at `SQLModel.metadata`, and generate the initial migration.
- [ ] Add a dev seed mechanism and the migration commands to `CLAUDE.md`.

## 4. Decisions you need to make (plan §20)

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

## 5. Later steps (for reference)

Step 3 auth and workspaces, then Step 4 workflow storage, Step 5 node registry, Step 6 execution persistence, Step 7 Celery workers, Step 8 Vue Flow editor, Step 9 monitoring UI and Step 10 the vertical-slice test. Docs and CI hardening follow.
