# Pivot

### Business Automation Platform

Pivot is a multi-tenant SaaS platform that lets organizations build, run, and monitor automations through a visual workflow editor. Connect your systems — email, databases, APIs, spreadsheets, messaging — and create workflows that trigger and act automatically, with no code required.

## What it does

- **Visual workflow builder** — drag-and-drop editor for building multi-step automations with branching logic
- **Event-driven triggers** — start workflows when an email arrives, a database row changes, an API returns new data, a webhook fires, or on a schedule
- **Automated actions** — send emails, write to spreadsheets, post to Slack/Teams/Discord, call APIs, query databases, generate reports
- **OAuth integrations** — connect Google (Gmail, Sheets, Drive), Slack, Microsoft (Outlook, Teams), and more with one-click authorization
- **Granular permissions** — custom roles per organization control who can see, edit, and run which automations
- **White-label theming** — dynamic color palettes, logos, and branding per organization
- **Monitoring dashboards** — execution stats, success rates, failure tracking, and audit logs

## Architecture

```
                 Vue 3 Frontend
                (themed per tenant)
                       │
                  FastAPI API
              (auth, RBAC, CRUD)
                       │
              ┌────────┴────────┐
              │                 │
        Celery Workers    Celery Beat
       (execute workflows) (poll triggers)
              │                 │
              └────────┬────────┘
                       │
              ┌────────┴────────┐
              │                 │
          PostgreSQL          Redis
        (all state,       (broker,
         encrypted         cache)
         credentials)
```

## Stack

| Component | Technology |
|---|---|
| Frontend | Vue 3, TypeScript, Vue Flow, Pinia |
| Backend | Python, FastAPI, SQLModel, Alembic |
| Database | PostgreSQL |
| Workers | Celery + Redis |
| Auth | JWT (access + refresh tokens) |
| Integrations | OAuth2, API keys, connection strings |
| Testing | Pytest, Vitest |
| Containers | Docker Compose |

## Quickstart

Requires Docker Desktop and Node.

```sh
npm run up      # starts Postgres, Redis, backend (:8000) and frontend (:5173) with hot reload
npm run down    # stops everything (data kept; npm run reset wipes volumes)
npm test        # runs all backend and frontend tests in containers
```

If a local Postgres already uses port 5432, set `POSTGRES_PORT=5433` in `.env`.

See `CLAUDE.md` for the full command reference.

## Project status

**Steps 1–3 complete**: repo foundation, database/migrations, JWT auth with workspace RBAC.

**Next**: custom roles and permissions, workflow storage, connection infrastructure, then the execution engine and visual editor.

See `docs/NEXT_STEPS.md` for the detailed checklist and `IMPLEMENTATION_PLAN.md` for the full spec.
