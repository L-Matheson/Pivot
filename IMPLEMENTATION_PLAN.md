# Pivot: First Implementation Plan

## 1. Purpose

This document defines the first implementation of Pivot: a small, working version that lets a user sign in, visually create and save a workflow, execute it asynchronously, and inspect the result.

The implementation should be a thin but complete vertical slice through the system. It is not a complete no-code platform, and it should not include the entire integration ecosystem from the beginning.

The target first milestone is:

> A signed-in user can open the workflow editor, add a simple HTTP request workflow, save it, run it, and view its execution status and node output.

## 2. Product Priorities

The first implementation should prioritize:

1. **Visual workflow editing**
2. **Workflow persistence**
3. **Workflow execution**
4. **Asynchronous workers**
5. **Execution monitoring**
6. **Authentication and permissions**
7. **REST API integration**
8. **Easy future extension**

The project should begin with personal use in mind while keeping the following SaaS-compatible concepts in place:

- User accounts
- Permissions
- Workflow ownership
- Organization or team boundaries
- Durable execution records
- Multi-host deployment support

## 3. Initial Assumptions

These assumptions are recommendations for the first implementation and can be changed before coding begins.

### 3.1 Deployment

- Local development will use Docker Compose.
- The same application structure should remain deployable to a hosted environment.
- PostgreSQL will store application data.
- Redis will act as the Celery broker and may later also support caching or real-time features.
- Celery workers will execute workflows outside the web request.

### 3.2 User Model

- Authentication will exist from the beginning.
- The initial permission model will distinguish at least:
  - Owners
  - Editors
  - Viewers
- A simple organization or workspace model will establish ownership boundaries.
- Personal workspaces should exist first.
- Team and SaaS features may expand later without redesigning workflow records.

### 3.3 Workflow Scope

The first workflow format will support:

- A manual trigger
- HTTP request nodes
- A transform or data node
- A condition node
- Linear and branching execution
- Structured node input and output
- One JSON workflow definition per saved workflow

The following features are intentionally deferred:

- Sub-workflows
- Workflow versioning
- Execution replay
- Scheduled triggers
- Webhook triggers
- Third-party notification integrations
- Database integrations
- Sports data integrations
- Collaborative real-time editing
- Node marketplace or plugin installation

### 3.4 Recommended Initial Architecture

The recommended monorepo structure is:

```text
Pivot/
  frontend/
  backend/
  docker/
  docs/
  .github/workflows/
  docker-compose.yml
  README.md
  IMPLEMENTATION_PLAN.md
```

The frontend and backend should be independently runnable, but the repository will provide Docker Compose for the complete local system.

## 4. Core Data Model

The initial database should represent the following concepts.

### 4.1 User

Suggested fields:

- `id`
- `email`
- `password_hash` or external identity provider ID
- `display_name`
- `is_active`
- `created_at`
- `updated_at`

### 4.2 Workspace

Suggested fields:

- `id`
- `name`
- `slug`
- `owner_user_id`
- `created_at`
- `updated_at`

A workspace prevents user-specific workflows from being directly accessible by unrelated users.

### 4.3 Workspace Membership

Suggested fields:

- `workspace_id`
- `user_id`
- `role`
- `created_at`

Initial roles:

- `owner`
- `editor`
- `viewer`

### 4.4 Workflow

Suggested fields:

- `id`
- `workspace_id`
- `name`
- `description`
- `definition`
- `is_active`
- `created_at`
- `updated_at`

`definition` should contain the visual graph and node configuration as validated JSON.

It should be stored as a JSON document or normalized graph tables depending on the implementation, but JSON should remain the canonical exported/imported format.

### 4.5 Workflow Execution

Suggested fields:

- `id`
- `workflow_id`
- `trigger_type`
- `status`
- `input`
- `output`
- `error`
- `started_at`
- `finished_at`
- `created_by`

Suggested statuses:

- `queued`
- `running`
- `succeeded`
- `failed`
- `cancelled`

### 4.6 Node Execution

Suggested fields:

- `id`
- `execution_id`
- `node_id`
- `node_type`
- `status`
- `input`
- `output`
- `error`
- `started_at`
- `finished_at`

This table enables node-level monitoring and debugging.

## 5. Workflow Definition Format

The workflow definition should use a simple, versioned JSON schema.

Example structure:

```json
{
  "schema_version": 1,
  "nodes": [
    {
      "id": "trigger_1",
      "type": "manual_trigger",
      "position": { "x": 100, "y": 200 },
      "config": {}
    },
    {
      "id": "http_1",
      "type": "http_request",
      "position": { "x": 320, "y": 200 },
      "config": {
        "method": "GET",
        "url": "https://example.com/api/status"
      }
    }
  ],
  "edges": [
    {
      "id": "edge_1",
      "source": "trigger_1",
      "target": "http_1"
    }
  ]
}
```

The format must include:

- A schema version for future migrations
- Stable node IDs
- Node types
- Node configuration
- Node positions for the visual editor
- Directed edges
- Optional edge conditions

Node configuration and input/output data should be validated with Pydantic models rather than treating arbitrary Python dictionaries as trusted types.

## 6. Extensible Node System

The workflow engine should not contain special hard-coded behavior for each future integration.

Instead, it should use a node registry:

```text
Node registry
  node type
  display metadata
  configuration schema
  input schema
  output schema
  executor
```

Adding a new node should ideally require:

1. A Pydantic configuration model
2. A Pydantic input/output model
3. An executor implementation
4. Registration with the node registry
5. Frontend node metadata or a shared configuration schema

The first implementation may include only:

- `manual_trigger`
- `http_request`
- `transform`
- `condition`

The engine should be designed so that future nodes such as schedule, webhook, database, Discord, email, or sports API nodes can be registered without changing workflow dependency resolution.

## 7. Workflow Engine Behavior

The engine will receive a validated workflow definition and an execution context.

The initial execution process will:

1. Load the workflow and verify workspace access.
2. Validate the workflow against the schema.
3. Create a workflow execution record with `queued` status.
4. Resolve node dependencies from edges.
5. Detect cycles before execution.
6. Submit the workflow execution task to Celery.
7. Mark the execution as `running`.
8. Determine which nodes are ready.
9. Execute ready nodes.
10. Pass each node's output to connected nodes.
11. Evaluate condition branches.
12. Continue until no executable nodes remain.
13. Persist node outputs and status.
14. Mark the workflow execution as `succeeded` or `failed`.

The engine should support:

- Topological dependency resolution
- Conditional branches
- Structured data propagation
- Persistent node execution records
- Failures and retries
- Concurrent execution of independent nodes

The first version does not need to support every concurrency optimization, but it should avoid embedding execution state only in memory.

## 8. Retry and Failure Strategy

Each node may define:

- Maximum retry attempts
- Retry delay
- Timeout
- Failure behavior

The initial HTTP node will:

- Enforce a timeout
- Reject unsupported or unsafe URLs if SSRF controls are added
- Retry configured transient HTTP status codes
- Store status, headers, and body in structured output
- Record failed requests without exposing secrets

Node and workflow failure rules should be explicit:

- `stop`: stop the workflow after failure
- `continue`: mark the node failed and continue if possible
- `retry`: retry the node according to node configuration

Secrets in node configuration must not be logged or returned in API responses.

## 9. API Plan

The FastAPI backend exposes routes under `/api` with no version segment. API versioning is handled through git and GitHub releases.

Example route groups:

```text
/api/auth
/api/workspaces
/api/workflows
/api/executions
/api/nodes
/api/users
```

### 9.1 Authentication

- Register and log in
- Read the current user
- Refresh or revoke sessions
- Logout
- Enforce workspace membership
- Enforce permissions per operation

The authentication implementation must decide between:

- Cookie-based sessions
- JWT access and refresh tokens
- External identity provider

Recommended for the first implementation: secure cookie-based sessions or short-lived access tokens with refresh tokens, rather than placing credentials directly in Vue state.

### 9.2 Workflow Routes

Minimum operations:

- List workflows
- Create a workflow
- Read a workflow
- Update a workflow
- Delete or archive a workflow
- Duplicate a workflow
- Export a workflow
- Import a workflow

### 9.3 Execution Routes

Minimum operations:

- Start a workflow execution
- List workflow executions
- Read execution details
- Read node executions
- Cancel an execution when supported
- Retry an execution when supported

## 10. Frontend Plan

The Vue 3 application should use TypeScript and Vue Flow.

Suggested structure:

```text
frontend/src/
  app/
  pages/
  components/
  features/
    auth/
    workspaces/
    workflows/
    editor/
    executions/
  composables/
  services/
  stores/
  types/
  styles/
```

Suggested routes:

- `/login`
- `/register`
- `/workspaces`
- `/workspaces/:workspaceId/workflows`
- `/workspaces/:workspaceId/workflows/:workflowId/edit`
- `/workspaces/:workspaceId/workflows/:workflowId/executions`
- `/executions/:executionId`

## 11. Visual Editor Requirements

The first editor should support:

- A canvas
- Pan and zoom
- Add-node panel
- Dragging nodes
- Connecting nodes
- Selecting nodes
- Deleting nodes
- Deleting edges
- Editing node configuration
- Saving workflow definitions
- Loading workflow definitions
- Executing the saved workflow
- Opening execution status

The UI does not need advanced features in the first milestone, but it should provide:

- Clear unsaved-change state
- Save feedback
- Execution feedback
- Validation errors
- Node status indicators
- Loading and empty states
- Permission-aware controls

## 12. Real-Time Monitoring

The first version may use WebSockets or polling.

Recommended initial approach:

1. Create an execution record immediately.
2. Queue a Celery task.
3. Return the execution ID.
4. Frontend polls execution status until completion.
5. Add WebSockets later for efficient real-time updates.

Once the architecture is stable, WebSockets can provide:

- Execution status changes
- Node status changes
- Worker activity
- Failure notifications

The REST API should remain the source of truth. WebSockets should be a notification layer, not the primary persistence mechanism.

## 13. Security Requirements

Security should be built into the foundation.

### 13.1 Authorization

- Never rely only on frontend permission checks.
- Every workflow and execution route must enforce workspace membership.
- Editors may edit and execute workflows.
- Viewers may inspect workflows and executions.
- Only owners or explicitly permitted users may manage memberships.

### 13.2 Secrets

- Secrets must use environment variables or a future secrets provider.
- Workflow secrets must not appear in workflow export data unless explicitly designed.
- Logs must redact credentials and authorization headers.
- Node configuration API responses must exclude secret values where appropriate.

### 13.3 HTTP Integrations

- Validate URLs.
- Block private, loopback, and link-local addresses unless an explicit safe mode is enabled.
- Restrict redirect behavior.
- Define allowed protocols.
- Set maximum response size.
- Apply request and execution timeouts.

### 13.4 General API Protection

- CORS allowlist
- Rate limiting
- Input validation
- CSRF protection if cookies are used
- SQL parameterization through SQLModel (SQLAlchemy core)
- Audit-sensitive operations

## 14. Testing Plan

Testing is a requirement for the initial implementation, not a later cleanup task.

### 14.1 Backend Tests

Use Pytest for:

- Pydantic workflow schema validation
- Authentication
- Permission checks
- Workflow CRUD
- Workflow execution creation
- Dependency resolution
- Cyclic workflow detection
- Branch evaluation
- Node execution
- HTTP node behavior
- Retry behavior
- Database migrations

The HTTP node tests should mock external requests instead of depending on the public internet.

### 14.2 Frontend Tests

Use Vitest for:

- Stores and API state
- Route guards
- Node configuration forms
- Workflow validation
- Add, move, connect, and delete nodes
- Save behavior
- Execution status display

Browser-level tests may be added after the editor stabilizes.

### 14.3 Integration Tests

The first integration test should prove the main vertical slice:

1. Register or log in
2. Create a workspace
3. Create a workflow
4. Add a manual trigger
5. Add an HTTP request node
6. Connect the nodes
7. Save the workflow
8. Start execution
9. Observe success or failure
10. Inspect node input and output

## 15. Local Docker Setup

The initial services should include:

- `frontend`
- `backend`
- `postgres`
- `redis`
- `celery-worker`
- `celery-beat` only if scheduling is implemented

The local setup should support:

- One-command startup
- Hot reload for frontend and backend
- Persistent PostgreSQL data
- Environment-based configuration
- A way to reset development data
- Worker log visibility

Database migrations will use Alembic.

## 16. CI/CD Foundation

The initial CI pipeline should run:

1. Backend formatting and lint checks
2. Backend tests
3. Frontend type checking
4. Frontend lint checks
5. Frontend tests
6. Docker build validation

A later CD pipeline may:

- Build versioned images
- Publish images to a registry
- Run migrations
- Deploy frontend and backend services
- Run database backup and rollback procedures

## 17. Implementation Sequence

### Step 1: Repository Foundation

Create the monorepo directories and baseline configuration.

Deliverables:

- Frontend package with Vue 3 and TypeScript
- FastAPI application package
- Docker Compose configuration
- Environment template
- PostgreSQL and Redis services
- Shared formatting and lint configuration
- README setup instructions

Acceptance criteria:

- PostgreSQL starts successfully
- Redis starts successfully
- Backend health endpoint returns success
- Frontend loads in a browser
- Both services run locally in Docker

### Step 2: Database and Migrations

Add SQLModel and Alembic. Use SQLModel `table=True` models for tables, and drop to SQLAlchemy core only where SQLModel has no equivalent (e.g. JSONB columns, indexes). Alembic autogenerates from `SQLModel.metadata`.

Deliverables:

- Database session setup
- Base models
- Initial migration
- Development seed mechanism
- Migration commands

Acceptance criteria:

- A clean database migrates successfully
- Re-running migrations is safe
- Database connection errors are clear

### Step 3: Authentication and Workspaces

Implement login and workspace boundaries.

Deliverables:

- User registration or initial setup
- Login and logout
- Current-user endpoint
- Workspace creation
- Workspace membership
- Role enforcement

Acceptance criteria:

- A user cannot access another workspace
- Viewer permissions are enforced
- Editor permissions are enforced
- Owner permissions are enforced

This step establishes the SaaS-ready ownership model before workflows are added.

### Step 4: Workflow Storage

Add the workflow JSON model and CRUD API.

Deliverables:

- Workflow Pydantic models
- SQLModel workflow model
- List, create, read, update, archive, duplicate, import, and export endpoints
- Workflow schema validation
- Frontend workflow service

Acceptance criteria:

- A workflow can be created and persisted
- Invalid workflow definitions are rejected
- Duplicate and archived workflows behave predictably
- Unauthorized users cannot access workflows

### Step 5: Node Registry and Workflow Schema

Create the extensible node system.

Deliverables:

- Node registry
- Node metadata endpoint
- Manual trigger executor
- HTTP request executor
- Transform executor
- Condition executor
- Cycle detection
- Dependency resolution

Acceptance criteria:

- Nodes register without modifying core orchestration logic
- Invalid graphs are rejected
- Cyclic graphs are rejected
- The HTTP executor can make a controlled request
- A condition can select an output branch

### Step 6: Execution Persistence

Create workflow and node execution records.

Deliverables:

- Execution database models
- Execution creation API
- Node execution creation API
- Execution status updates
- Execution detail endpoints
- Retry and cancellation records

Acceptance criteria:

- An execution record exists before processing
- Every node execution has a status
- Final execution status reflects node outcomes
- Input, output, and errors can be retrieved safely

### Step 7: Celery Workers

Move workflow execution off the API process.

Deliverables:

- Celery application setup
- Redis broker configuration
- Workflow execution task
- Worker service
- Task serialization safeguards
- Task retry configuration

Acceptance criteria:

- Starting a workflow returns quickly
- Celery executes the workflow asynchronously
- Worker failures do not corrupt execution state
- Concurrent executions do not overwrite each other

### Step 8: Visual Workflow Editor

Build the Vue Flow editor.

Deliverables:

- Workflow list page
- Editor canvas
- Add-node panel
- Node configuration forms
- Edge creation and deletion
- Save and load behavior
- Unsaved-change indicator
- Node palette metadata from backend

Acceptance criteria:

- A user can add and configure nodes
- A user can connect nodes
- Invalid graphs show useful validation feedback
- A workflow reload reproduces the saved canvas
- Permission restrictions disable unauthorized actions

### Step 9: Execution and Monitoring UI

Add execution management and observation.

Deliverables:

- Run workflow action
- Execution list
- Execution detail page
- Node status display
- Node input/output inspector
- Error display
- Refresh or polling behavior

Acceptance criteria:

- The user can run a saved workflow
- The UI updates until the execution completes
- Users can identify which node failed
- Inputs and outputs are readable
- Failed executions show actionable errors

### Step 10: First Complete Vertical-Slice Test

Test and demonstrate the complete first milestone.

The demo workflow should:

1. Start with a manual trigger
2. Make an HTTP GET or POST request
3. Transform or inspect the response
4. Apply a condition
5. Save and execute successfully

Acceptance criteria:

- A signed-in user can complete the workflow without using the API directly
- The workflow remains persisted after reload
- Execution history remains available
- Node output is visible
- The workflow can fail and recover without corrupting state

### Step 11: Documentation and Developer Experience

After the vertical slice works, document how to extend it.

Deliverables:

- Local setup guide
- Environment variable guide
- Workflow format documentation
- Node implementation guide
- API documentation
- Database migration guide
- Deployment guide
- Troubleshooting guide

### Step 12: CI and Release Hardening

Once the core is stable:

- Enable CI checks
- Containerize all services
- Add automated migrations
- Add backup documentation
- Add release versioning
- Add a smoke test that starts the full system

This is the boundary for the initial implementation milestone.

## 18. Suggested First Demo Workflow

A practical first demo is a "service monitor":

```text
Manual Trigger
  -> HTTP Request
  -> Transform Response
  -> Condition
      -> Success branch
      -> Failure branch
```

The HTTP node should check an API endpoint and return status information. The transform node should extract fields such as status code or availability. The condition node should branch based on whether the response is successful.

This proves:

- Manual triggering
- External API communication
- Data propagation
- Conditional branching
- Execution persistence
- Node-level monitoring

## 19. Proposed Milestones

### Milestone A: Foundation

- Monorepo
- Docker Compose
- PostgreSQL
- Redis
- FastAPI
- Vue
- Health checks
- CI baseline

### Milestone B: Auth and Storage

- Authentication
- Workspaces
- Permissions
- Workflow CRUD
- Database migrations

### Milestone C: Engine

- Workflow schema
- Node registry
- Dependency resolution
- Branching
- Execution persistence
- Celery workers

### Milestone D: Editor

- Workflow canvas
- Nodes and edges
- Configuration forms
- Save and load
- Permission-aware UI

### Milestone E: Monitoring

- Execution list
- Execution detail
- Node status
- Input/output inspection
- Polling

### Milestone F: Release Candidate

- End-to-end test
- Documentation
- Docker deployment
- CI/CD
- Security hardening

## 20. Decisions to Confirm Before Coding

The following choices may affect implementation:

1. **Authentication strategy**
   - Secure cookie sessions
   - JWT
   - External identity provider

2. **Monorepo package management**
   - npm and Python dependency files
   - pnpm or npm
   - Poetry or plain requirements files
   - **Decided (backend):** uv with `pyproject.toml` + `uv.lock`

3. **Workflow graph storage**
   - JSON-only workflow definition
   - Normalized database nodes and edges
   - Hybrid approach

4. **Execution data storage**
   - PostgreSQL only
   - PostgreSQL with Redis status/cache
   - PostgreSQL plus object storage for large outputs

5. **First HTTP node behavior**
   - Basic request/response
   - Headers and authentication
   - Credentials and secret references

6. **Permission model**
   - Workspace role only
   - Per-workflow permissions
   - Both role-based and resource-based permissions

7. **Frontend editor scope**
   - Full node palette
   - Small first node palette
   - Schema-generated configuration forms

8. **Real-time monitoring**
   - Polling first
   - WebSockets from the beginning

These decisions do not require final answers before repository scaffolding begins, but they should be made explicitly before the related implementation step starts.
