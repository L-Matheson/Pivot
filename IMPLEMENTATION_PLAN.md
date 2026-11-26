# Pivot: Implementation Plan

## 1. Purpose

Pivot is a multi-tenant SaaS business automation platform. Organizations sign up, connect their systems (email, databases, APIs, spreadsheets, messaging), and build visual workflows that trigger and act automatically. The target user is non-technical — a business user who can drag, drop, and configure without writing code.

The platform is comparable to Zapier, Make, or n8n, but self-branded per tenant, with granular permission tiers so sensitive automations are invisible to unauthorized staff.

### First milestone target

> A signed-in user connects a Gmail account, creates a workflow that triggers when an email with a specific label arrives, and the workflow sends a notification and writes a row to a Google Sheet — all configured through a visual editor with no code.

## 2. Product priorities

1. **Visual workflow builder** — drag-and-drop, non-technical audience
2. **Integration ecosystem** — OAuth connectors for major services, API keys as fallback
3. **Event-driven triggers** — email labels, database changes, webhooks, scheduled polling
4. **Automated actions** — send email, write to spreadsheet, send notification, call API
5. **Branching and conditional logic** — if/else paths, parallel branches from day one
6. **Multi-tenant isolation** — each organization's data, connections, and workflows are fully separated
7. **Granular permissions** — fixed admin role + custom roles per organization with automation-level visibility
8. **White-label theming** — dynamic color palettes and branding per tenant
9. **Operational dashboards** — stats pages for monitoring workflows, executions, and platform health
10. **Asynchronous execution** — background workers with persistent state

## 3. Architecture overview

### 3.1 Deployment model

Multi-tenant SaaS. All tenants share the same infrastructure with row-level data isolation through the workspace/organization model. Each organization gets its own branding, roles, and connected services.

### 3.2 Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3, TypeScript, Vue Flow (editor), Pinia (state), Vue Router |
| Backend | Python, FastAPI, SQLModel, Alembic, Pydantic, Celery |
| Database | PostgreSQL (all durable state) |
| Broker / Cache | Redis (Celery broker, real-time pub/sub, caching) |
| Background workers | Celery (workflow execution, polling triggers, scheduled tasks) |
| OAuth / Secrets | Encrypted credential store in PostgreSQL, OAuth2 flows per provider |
| Real-time | WebSockets (notification layer, polling REST remains source of truth) |
| Containerization | Docker Compose (dev), production-ready container images |

### 3.3 Repository layout

```text
Pivot/
  frontend/          # Vue 3 SPA
  backend/           # FastAPI + Celery
  docker/            # Dockerfiles
  docs/              # Architecture, guides
  .github/workflows/ # CI/CD
  docker-compose.yml
```

## 4. Data model

### 4.1 Multi-tenancy and identity

**User** — id, email, password_hash, display_name, is_active, created_at, updated_at

**Workspace** (organization/tenant) — id, name, slug, owner_user_id, theme_config (JSONB), settings (JSONB), created_at, updated_at

**WorkspaceMembership** — workspace_id, user_id, role_id, created_at

**Role** — id, workspace_id (nullable — null = system role), name, is_system (bool), permissions (JSONB), created_at, updated_at

System roles (workspace_id=null, is_system=true): `admin` (full access), `member` (default). Workspace custom roles carry a permissions object that grants/denies visibility and actions on automation folders/tags.

### 4.2 Permissions model

The permissions JSONB on each role defines:

```json
{
  "automations": {
    "view": ["*"],
    "edit": ["folder:finance", "tag:hr"],
    "execute": ["folder:finance"],
    "manage": false
  },
  "connections": { "view": true, "manage": false },
  "members": { "view": true, "manage": false },
  "settings": { "view": false, "manage": false },
  "stats": { "view": true }
}
```

The `admin` system role bypasses all checks. Folder and tag-based scoping lets organizations hide sensitive automations (e.g., financial workflows invisible to base employees). Backend enforces all permission checks; frontend uses them only for UI gating.

### 4.3 Connections (integrations)

**Connection** — id, workspace_id, provider (e.g. `gmail`, `google_sheets`, `slack`, `postgres`), name, auth_type (`oauth2` | `api_key` | `connection_string`), credentials_encrypted (bytea), scopes, status, connected_by_user_id, created_at, updated_at

**ConnectorRegistry** — provider slug, display name, icon, auth_type, oauth config (client_id/secret from env), available scopes, available triggers, available actions

Credentials are encrypted at rest using a per-workspace key derived from `PIVOT_ENCRYPTION_KEY`. OAuth tokens are auto-refreshed. Connection strings and API keys are stored encrypted, never logged, never returned in API responses.

### 4.4 Workflows

**Workflow** — id, workspace_id, name, description, folder, tags (array), definition (JSONB), is_active, created_by, created_at, updated_at

**WorkflowDefinition** (the JSONB):
```json
{
  "schema_version": 1,
  "nodes": [
    {
      "id": "trigger_1",
      "type": "email_trigger",
      "position": { "x": 100, "y": 200 },
      "config": {
        "connection_id": "uuid",
        "label_filter": "invoices"
      }
    },
    {
      "id": "action_1",
      "type": "send_notification",
      "position": { "x": 400, "y": 200 },
      "config": { "channel": "slack", "message": "New invoice received" }
    }
  ],
  "edges": [
    { "id": "e1", "source": "trigger_1", "target": "action_1" }
  ]
}
```

### 4.5 Executions

**WorkflowExecution** — id, workflow_id, trigger_type, trigger_data (JSONB), status, started_at, finished_at, created_by, error

**NodeExecution** — id, execution_id, node_id, node_type, status, input (JSONB), output (JSONB), error, started_at, finished_at

Statuses: `queued`, `running`, `succeeded`, `failed`, `cancelled`.

### 4.6 Theming

**Workspace.theme_config** (JSONB):
```json
{
  "primary_color": "#2563EB",
  "secondary_color": "#7C3AED",
  "accent_color": "#F59E0B",
  "logo_url": null,
  "favicon_url": null,
  "app_name": "Acme Automations"
}
```

Frontend reads theme from workspace settings on login and applies CSS custom properties globally. Every color in the UI derives from the palette — no hardcoded brand colors.

### 4.7 Audit log

**AuditEntry** — id, workspace_id, user_id, action, resource_type, resource_id, metadata (JSONB), created_at

Tracks connection changes, workflow modifications, permission changes, and execution events for compliance and debugging.

## 5. Connector and node system

### 5.1 Connector registry

Each integration provider is a connector that declares:
- Provider slug and display metadata
- Auth configuration (OAuth2 endpoints, scopes, or API key schema)
- Available triggers (events that start a workflow)
- Available actions (operations a workflow step can perform)

### 5.2 Node types

**Triggers** (start a workflow):
- `email_trigger` — email received with label/filter match
- `webhook_trigger` — incoming HTTP POST to a generated URL
- `schedule_trigger` — cron expression
- `database_trigger` — polling for new/changed rows
- `api_poll_trigger` — periodic check of an API endpoint or website
- `manual_trigger` — user clicks "Run"

**Actions** (perform an operation):
- `send_email` — send via connected email account
- `write_spreadsheet` — append/update rows in Google Sheets
- `send_notification` — Slack, Teams, Discord, or in-app
- `http_request` — arbitrary HTTP call with response handling
- `database_query` — read/write to a connected database
- `transform` — map, filter, format data between steps
- `delay` — wait a configured duration before continuing
- `create_record` — write to a connected CRM/database/service

**Logic** (control flow):
- `condition` — if/else branching based on expressions
- `switch` — multi-branch routing
- `loop` — iterate over a list from a previous step
- `parallel` — fan-out to multiple branches, fan-in on completion

**Utility**:
- `log` — write to execution log for debugging
- `set_variable` — store a value for use by later steps
- `error_handler` — catch and handle failures from upstream nodes

### 5.3 Adding a new node

Each node type provides:
1. A Pydantic config model (what the user configures)
2. Pydantic input/output models (data schema)
3. An executor function
4. Registry metadata (display name, icon, category, description)
5. Frontend form schema (auto-generates the config UI)

The engine never contains node-specific logic. Adding a node is registration, not engine modification.

## 6. Integration strategy

### 6.1 OAuth connectors (priority)

For major services, users click "Connect" and authorize through OAuth2:
- **Google** (Gmail, Sheets, Drive, Calendar)
- **Slack**
- **Microsoft** (Outlook, Teams, OneDrive, Excel)
- **Discord**

OAuth client credentials live in environment variables (`PIVOT_GOOGLE_CLIENT_ID`, etc.), never in the database. Per-user tokens are encrypted in the Connection table.

### 6.2 API key / connection string fallback

For services without OAuth or for custom integrations:
- API keys (entered by user, stored encrypted)
- Database connection strings (Postgres, MySQL, MongoDB)
- Webhook URLs

### 6.3 Website / API monitoring

The `api_poll_trigger` node runs on Celery Beat at a configured interval:
- Fetches a URL and compares the response to the previous fetch
- Detects changes (content diff, status code change, specific JSON field change)
- Fires the workflow when a change is detected
- SSRF protections apply: block private/loopback/link-local addresses

## 7. Permissions deep dive

### 7.1 System roles

| Role | Scope | Description |
|---|---|---|
| `admin` | Bypasses all checks | Full access to everything in the workspace |
| `member` | Default | Access governed by their custom role assignment |

### 7.2 Custom roles

Each workspace can define custom roles (e.g., "Finance Team", "Marketing", "Support Lead"). Each custom role specifies:

- Which automation **folders** and **tags** are visible
- Whether the user can view, edit, execute, or manage automations in those scopes
- Whether the user can view/manage connections, members, or settings
- Whether the user can view stats/dashboards

### 7.3 Enforcement

- Backend: every API route checks the user's effective permissions before returning data
- Workflow list endpoints filter results based on folder/tag visibility
- Connection credentials are never returned to users who lack `connections.manage`
- Frontend: hides UI elements the user cannot access (cosmetic only — backend is authoritative)

## 8. Theming and white-labeling

The frontend theming system is fully dynamic:

- **CSS custom properties** — all colors, border radii, and spacing derive from workspace theme config
- **Logo and app name** — displayed in the sidebar and login page, pulled from workspace settings
- **Favicon** — configurable per workspace
- **Color palette** — primary, secondary, accent, success, warning, error, plus auto-generated light/dark variants
- **Dark mode** — supported from the start, theme config defines both light and dark palettes
- **Settings UI** — workspace admins can change the palette live with a color picker and see a preview

No hardcoded brand colors anywhere in the frontend. Every color reference uses a CSS variable.

## 9. Stats and monitoring dashboards

### 9.1 Workflow stats

- Total workflows (active/inactive)
- Executions over time (line chart)
- Success/failure rate (donut chart)
- Average execution duration
- Most-triggered workflows
- Workflows with highest failure rate

### 9.2 Execution stats

- Recent executions table with status, duration, trigger type
- Execution timeline (Gantt-style per node)
- Node-level success/failure breakdown
- Error frequency and categories

### 9.3 Platform stats (admin only)

- Active connections by provider
- Users and roles
- Storage and execution usage
- Audit log viewer

## 10. Security requirements

### 10.1 Authentication

- JWT with short-lived access tokens (30 min) and refresh tokens (7 days)
- `PIVOT_SECRET_KEY` rejected if default in production
- Issuer/audience validation on all tokens
- Malformed token subjects return 401, not 500
- Password length bounded (8–128 characters, bcrypt safe range)
- Swagger docs disabled in production (`debug=False`)

### 10.2 Secrets and credentials

- OAuth tokens and API keys encrypted at rest using `PIVOT_ENCRYPTION_KEY`
- Credentials never logged, never returned in API responses
- Workflow exports strip connection credentials (export connection_id references, not secrets)
- Audit log tracks connection creation/modification

### 10.3 Network safety

- HTTP/API poll nodes: validate URLs, block private/loopback/link-local addresses (SSRF)
- Restrict redirect chains, cap response size, enforce timeouts
- Database connections: validate connection strings, enforce TLS where available
- CORS allowlist, rate limiting, input validation

### 10.4 Multi-tenant isolation

- Every database query is scoped to the authenticated user's workspace
- No cross-workspace data access is possible through the API
- Background workers validate workspace context before executing
- Connection credentials are workspace-scoped and encrypted per workspace

## 11. Implementation sequence

### Phase 1: Core platform (Steps 1–6) — DONE through Step 3

Steps 1–3 are complete: repo foundation, database/migrations, auth/workspaces.

#### Step 4: Custom roles and permissions

Extend the existing workspace role system to support custom roles.

Deliverables:
- Role model with JSONB permissions
- System roles (admin, member) seeded on workspace creation
- Custom role CRUD API
- Permission checking utilities
- Folder and tag-based automation scoping
- Migration and tests

#### Step 5: Workflow storage

Add the workflow model and CRUD API.

Deliverables:
- Workflow Pydantic models (definition schema with schema_version, nodes, edges)
- SQLModel Workflow table with folder and tags fields
- CRUD API: list (filtered by permissions), create, read, update, archive, duplicate, import, export
- Workflow schema validation (reject cycles, validate node types)
- Permission-aware filtering on list endpoints
- Migration and tests

#### Step 6: Connection infrastructure

Build the encrypted credential store and connector registry.

Deliverables:
- Connection model with encrypted credentials column
- Encryption utilities (PIVOT_ENCRYPTION_KEY)
- Connector registry (provider definitions)
- Connection CRUD API (create, list, test, delete — credentials never returned)
- OAuth2 flow endpoints (authorize URL, callback handler, token refresh)
- API key and connection string storage
- Google OAuth connector (Gmail + Sheets — first provider)
- Migration and tests

### Phase 2: Execution engine (Steps 7–9)

#### Step 7: Node registry and engine

Build the extensible node system and execution engine.

Deliverables:
- Node registry with config/input/output Pydantic models per node type
- Node metadata API endpoint (`/api/nodes`)
- Initial node executors: manual_trigger, email_trigger, http_request, send_email, write_spreadsheet, send_notification, transform, condition
- Topological dependency resolution
- Cycle detection
- Branching execution (if/else, parallel)
- Structured data propagation between nodes
- Tests for each node executor (mocked external calls)

#### Step 8: Execution persistence

Create execution and node execution records.

Deliverables:
- WorkflowExecution and NodeExecution models
- Execution creation API
- Execution detail and list endpoints (permission-filtered)
- Node execution records with input/output/error
- Status management (queued → running → succeeded/failed)
- Retry and cancellation support
- Migration and tests

#### Step 9: Celery workers and triggers

Move execution off the API process and implement trigger polling.

Deliverables:
- Celery app configuration with Redis broker
- Workflow execution task
- celery-worker Docker service
- celery-beat for scheduled and polling triggers
- Email trigger implementation (poll Gmail for labeled messages)
- Schedule trigger (cron expressions)
- API poll trigger (website/endpoint monitoring)
- Task retry and failure handling
- Tests

### Phase 3: Frontend (Steps 10–13)

#### Step 10: Theming infrastructure

Build the dynamic theming system before any UI pages.

Deliverables:
- CSS custom property system (all colors from variables)
- Theme provider composable that reads workspace theme_config
- Light and dark mode support
- Theme settings API (admin-only update)
- Color picker in workspace settings
- Logo and app name from workspace config

#### Step 11: Auth and workspace UI

Deliverables:
- Login and registration pages
- Workspace selector (users may belong to multiple)
- Workspace settings page (name, theme, roles)
- Member management page (invite, assign roles)
- Custom role editor
- Vue Router with auth guards
- Pinia stores for auth and workspace state

#### Step 12: Visual workflow editor

Build the Vue Flow editor.

Deliverables:
- Workflow list page (filtered by folder/tag permissions)
- Editor canvas with pan/zoom
- Node palette sidebar (from backend registry)
- Drag-and-drop node placement
- Edge creation and deletion
- Node configuration forms (auto-generated from node schema)
- Connection selector in node config (pick from workspace connections)
- Branching visualization (if/else paths, parallel branches)
- Save, load, unsaved-change indicator
- Permission-aware controls (view-only for viewers)

#### Step 13: Execution monitoring UI

Deliverables:
- Run workflow action from editor
- Execution list page with status, duration, trigger info
- Execution detail page with node-by-node status
- Node input/output inspector
- Error display with actionable messages
- Polling for status updates (WebSocket notification layer later)
- Execution timeline visualization

### Phase 4: Dashboards and polish (Steps 14–16)

#### Step 14: Stats dashboards

Deliverables:
- Workflow stats page (execution counts, success rates, durations)
- Execution analytics (trends over time, failure categories)
- Admin platform stats (connections, users, storage)
- Audit log viewer (admin only)
- Charts using a lightweight library (Chart.js or similar)

#### Step 15: Connections UI

Deliverables:
- Connections page (list connected services, status indicators)
- "Connect" flow for OAuth providers (Google, Slack, Microsoft)
- API key and connection string input forms
- Connection test button
- Connection usage display (which workflows use this connection)

#### Step 16: Documentation and CI/CD

Deliverables:
- Local setup guide
- Environment variable reference
- Connector development guide (how to add a new provider)
- Node development guide (how to add a new node type)
- API documentation
- GitHub Actions CI (lint, test, typecheck, Docker build)
- Production deployment guide

## 12. Decisions

| Decision | Status | Choice |
|---|---|---|
| Authentication strategy | Decided | JWT (access + refresh tokens) |
| Permission model | Decided | System roles (admin/member) + custom roles with JSONB permissions, folder/tag scoping |
| Deployment model | Decided | Multi-tenant SaaS |
| Integration auth | Decided | OAuth first for major providers, API keys as fallback |
| First vertical slice | Decided | Email trigger → notification + spreadsheet write |
| Target user | Decided | Non-technical business users |
| Workflow branching | Decided | If/else and parallel branches from the start |
| Billing | Deferred | Build product first, add subscription tiers later |
| Workflow graph storage | Decided | JSON-only (JSONB column) |
| Execution data storage | Decided | PostgreSQL only (add Redis cache later if needed) |
| Real-time monitoring | Decided | Polling first, WebSockets as notification layer later |
| Frontend package manager | Decided | npm |
| Backend package manager | Decided | uv (pyproject.toml + uv.lock) |

## 13. Suggested additional automations

Common business automation actions to include in the node library beyond the basics:

**Communication**: send SMS (Twilio), post to Teams/Discord channel, create a support ticket, send a push notification

**Data**: generate PDF report, merge/split spreadsheet data, format and validate data, deduplicate records

**CRM and sales**: create/update CRM contact, log activity, send follow-up email sequence, assign lead

**IT and DevOps**: create Jira/Linear ticket, trigger CI/CD pipeline, restart a service, check SSL certificate expiry

**Finance**: generate invoice, reconcile records, flag transactions over threshold, send payment reminder

**HR**: send onboarding checklist, schedule review reminder, update directory entry

These are future node types that follow the same registration pattern — no engine changes required.
