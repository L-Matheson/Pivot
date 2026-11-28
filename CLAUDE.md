# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

Pivot is a multi-tenant SaaS business automation platform (Vue 3 + FastAPI + Celery). Organizations connect their systems (email, databases, APIs, spreadsheets, messaging) and build visual workflows that trigger and act automatically. The target user is non-technical — a drag-and-drop visual builder, no code.

`IMPLEMENTATION_PLAN.md` is the authoritative spec. Currently: FastAPI backend with JWT auth (split-token: in-memory access + httpOnly cookie refresh), User/Workspace/WorkspaceMembership/Role/Workflow models, PostgreSQL via SQLModel + Alembic with auto-migrations, Vue 3 + TS frontend (Vite) with VueFlow workflow editor, Docker Compose dev stack. No Celery or connections yet.

**Next step:** Step 6 — Connection Infrastructure (encrypted credential store, connector registry, OAuth2 flow, Google OAuth connector). See `docs/NEXT_STEPS.md`.

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

`app/main.py` builds the app with `create_app()`. Each resource is a **package** (folder) in `app/api/` — not a flat `.py` file. The package structure:

- `routes.py` — route handler functions on an `APIRouter(prefix="/<resource>", tags=[...])`.
- `commands.py` — shared business logic used by multiple routes (e.g. "get entity or 404"). Only when needed.
- `utils.py` — pure helper functions (no DB session, no request context). Only when needed.
- `__init__.py` — re-exports `router` from `routes.py`. For multi-file splits, combines sub-routers via `include_router`.

For packages split into multiple route files (e.g. `connections/` with `routes.py` + `oauth.py`): each sub-module defines its own `APIRouter` with the full prefix, and `__init__.py` combines them on a prefix-less wrapper.

`app/api/__init__.py` mounts all packages under `/api`. Register a new module there. The URL has no version segment, because API versioning is handled through git and GitHub releases, not URL paths or folders. Settings live in `app/core/config.py` (pydantic-settings). Env vars use the `PIVOT_` prefix and can also come from `backend/.env`, e.g. `PIVOT_CORS_ORIGINS='["http://localhost:5173"]'`.

Database: `app/core/db.py` provides a lazy engine (created on first use, not at import time), a `get_session` dependency, and a `SessionDep` type alias. Table models go in `app/models/` as SQLModel `table=True` classes; each new model file must be imported in `app/models/__init__.py` so Alembic sees it. Shared field factories (`id_field`, `created_at_field`, `updated_at_field`) live in `app/models/base.py`. Alembic config is in `backend/alembic.ini`; `alembic/env.py` reads `PIVOT_DATABASE_URL` from settings. Migrations in `alembic/versions/` are auto-generated and auto-applied by `npm run up`.

Authentication: JWT-based with a split-token architecture. The **refresh token** (30 days) is stored in an httpOnly `SameSite=Lax` cookie (`pivot_refresh`) — JavaScript cannot access it. The **access token** (15 min) is stored in-memory on the frontend (a module-level variable in `client.ts`) and sent as `Authorization: Bearer` on each request — it is never in localStorage or cookies. On 401, the frontend calls `POST /api/auth/refresh` (the browser sends the refresh cookie automatically), receives a new access token in the response body, and retries. A background timer refreshes the access token 60 seconds before expiry so users stay logged in seamlessly. On page load, `restoreSession()` in the auth store uses the refresh cookie to get a fresh access token. Cookie helpers live in `app/core/cookies.py`. Token creation/verification and password hashing are in `app/core/security.py`; FastAPI auth dependencies in `app/core/auth.py`. Protected routes use `CurrentUserDep` (extracts user from Bearer header). Auth routes at `/api/auth/` (register, login, refresh, logout, me); workspace routes at `/api/workspaces/`. Settings: `PIVOT_SECRET_KEY`, `PIVOT_JWT_ALGORITHM`, `PIVOT_JWT_ISSUER`, `PIVOT_JWT_AUDIENCE`, `PIVOT_ACCESS_TOKEN_EXPIRE_MINUTES`, `PIVOT_REFRESH_TOKEN_EXPIRE_DAYS`, `PIVOT_COOKIE_SECURE`, `PIVOT_COOKIE_SAMESITE`, `PIVOT_COOKIE_NAME_REFRESH`. Swagger docs are disabled when `PIVOT_DEBUG=false`.

The frontend calls the backend only through relative `/api/...` URLs in `src/services/api/`. API functions take an injectable `fetchFn` so they can be unit-tested without a server.

## Frontend code organization

- **Types** go in `src/types/`, one file per domain (`auth.ts`, `workspace.ts`, `health.ts`). If an interface is used by more than one file, it must live here — not inline in a component or service.
- **API route functions** go in `src/services/api/`, one file per domain (`auth.ts`, `workspaces.ts`, `health.ts`). The barrel `index.ts` re-exports everything so callers can still import from `@/services/api`. Shared plumbing (`request`, `ApiError`) lives in `client.ts`.
- **Composables** go in `src/composables/`, one file per domain. Each composable file groups all CRUD operations for its domain (queries + mutations). GET requests that return data the UI needs to keep fresh use TanStack `useQuery` for automatic caching and invalidation. Mutations use `useMutation` and invalidate related queries on success.
- **Pinia stores** are reserved for client-side selection state (e.g. "which workspace am I in") — not for data fetching, which belongs in composables.
- **Reuse rule:** if an API function, interface, or composable is used in more than one file, it must be extracted into its own domain file and imported — never duplicated inline.
- **No prop drilling.** When data or callbacks would pass through an intermediate component that doesn't use them, choose one of: (1) `provide`/`inject` for page-scoped state shared with deeply nested descendants — pair a `provideXxx()` call in the ancestor with a `useXxx()` inject helper in the consumer, both in the same composable file; (2) a shared composable when the state is derived from an external source (API, browser) rather than owned by a single page; (3) a Pinia store when the state is app-global (current user, current workspace). Never relay a prop or re-emit an event through a component that is just passing it along. **Exception:** passing data through 1–3 levels is fine when intermediate components have a legitimate relationship or responsibility (e.g. a Section that resolves `.has()` before passing a boolean to a Card). Don't introduce provide/inject for shallow chains — that's overkill.

- **v-if chain limit.** `v-if / v-else-if / v-else` chains are acceptable for 2–4 mutually exclusive UI states. Beyond that, use a `Record<string, Component>` lookup map and `<component :is>` with a computed resolver. Each variant becomes its own SFC in a co-located folder (e.g. `components/config/`), and the index barrel exports the map. New variants are added by creating a component and adding one line to the map — no template changes in the parent.
- **Readable names and file sections.** Variable names must be plain English and state what they hold — `lowerSearchQuery` not `q`, `matchingWorkspaces` not `res`. Within each `<script setup>` block, group declarations under minimal lowercase section comments: `// routing`, `// data`, `// ui state`, `// computed`, `// actions`. When several computed/watch/function declarations are stacked, add a one-line comment above the group explaining *why* they exist as a set (e.g. "One filtered list per section so the template can show/hide each independently"). Watchers (`watch`, `onMounted`, `onUnmounted`) go at the bottom of the `<script setup>` block, after all functions and constants.

Before implementing anything, read the relevant section of `IMPLEMENTATION_PLAN.md` and check `docs/NEXT_STEPS.md`, the user-facing checklist. Update it when a step or decision is completed.

## Planned stack and layout

- `frontend/`: Vue 3, TypeScript, Vue Flow (editor), Pinia (selection state), TanStack Query (data fetching), Vue Router, Vitest. Feature folders under `src/features/`.
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
- **Dark mode hover pairing.** Every `hover:bg-<token>` must include a matching `hover:text-<token>-foreground` so text stays legible when the background changes — workspace theming can override `--accent` / `--primary` to arbitrary colors. Never use partial-opacity hover backgrounds (`hover:bg-accent/50`); use the full token with its foreground pair instead. Buttons get `ring-offset-background` on their focus ring so the offset gap matches the page background in both modes.
- **Reusable UI components.** Use the shared components in `src/components/ui/` (`UiButton`, `UiCard`, `UiInput`, `UiLabel`, `UiAvatar`, `UiSpinner`, `UiSeparator`, `UiEmptyState`) instead of rebuilding equivalent markup inline. Add a new shared component when the same pattern (>10 lines) appears in 3+ places.

## Security requirements

- Never log secrets or return them in API responses or workflow exports. Redact auth headers in logs.
- HTTP/API poll nodes: validate URLs, block private/loopback/link-local addresses (SSRF), restrict redirects, cap response size, enforce timeouts.
- JWT auth uses short-lived in-memory access tokens (15 min) and httpOnly-cookie refresh tokens (30 days). Access tokens are never stored in localStorage or cookies. Refresh tokens are httpOnly, Secure (in production), SameSite=Lax — JavaScript cannot read them. `PIVOT_SECRET_KEY` is rejected if default when `PIVOT_DEBUG=false`. Tokens include issuer/audience claims. Refresh endpoint rotates the refresh cookie on each use.
- Encrypted credential store for all connection secrets (OAuth tokens, API keys, connection strings).
- CORS allowlist. Rate limiting. Input validation. Swagger docs disabled in production.

## Testing expectations

Tests are part of each step, not a later cleanup. Node executor tests must mock external calls and never hit the public internet. Integration tests prove the vertical slice end-to-end.
