# Pivot
### Open-Source Visual Workflow Automation Platform

Pivot is an open-source workflow automation platform designed to make complex, multi-step processes easier to build, execute, and monitor.

Using a visual, node-based editor, users can construct workflows by connecting triggers, operations, conditions, and integrations without needing to write application code. Workflows can interact with external APIs, process and transform data, query databases, send notifications, and execute scheduled tasks.

The platform is designed around a modular execution engine that supports asynchronous processing, conditional branching, persistent execution state, and extensible integrations.

## Core Features

### Visual Workflow Builder
- Drag-and-drop node-based workflow editor.
- Connect operations to define execution paths and dependencies.
- Configure nodes through dynamic configuration interfaces.
- Support conditional branching and multiple execution paths.
- Save, edit, duplicate, and manage workflows.
- Import and export workflow definitions.

### Workflow Execution Engine
- Execute workflows manually, on schedules, or through external triggers.
- Asynchronous execution using background workers.
- Resolve node dependencies and manage execution order.
- Pass structured data between connected nodes.
- Support conditional execution and branching.
- Maintain persistent execution state.
- Handle execution failures, timeouts, and retries.
- Support concurrent workflow executions.

### Integrations and Extensibility
A modular integration system allows the platform to interact with external services and data sources.

Planned integration categories include:

- **HTTP / REST APIs:** Make requests, process responses, and interact with external services.
- **Databases:** Execute queries and retrieve or persist structured data.
- **Notifications:** Send messages through Discord, email, and other notification providers.
- **Sports Data:** Retrieve schedules, game statuses, scores, and statistical information.
- **Webhooks:** Receive external events and trigger workflows.
- **Custom Integrations:** Extend the platform with independently developed nodes and integrations.

### Execution Monitoring
- View workflow execution history.
- Monitor individual node execution states.
- Inspect node inputs, outputs, and execution results.
- Track execution durations and failures.
- Identify and troubleshoot failed operations.
- Retry failed executions where appropriate.
- Monitor background worker activity.

## Architecture

Pivot is designed around a decoupled frontend, backend, and asynchronous execution system.

```text
                 Vue 3 Frontend
                       |
                  FastAPI API
                       |
              Workflow Management
                       |
              Workflow Scheduler
                       |
                  Redis Queue
                       |
              Execution Workers
                       |
              Workflow Engine
                       |
          +------------+------------+
          |            |            |
       API Nodes    Logic Nodes   Integrations
          |            |            |
       External     Data Flow     External
       Services     Processing    Services
```

The workflow engine is responsible for execution orchestration, dependency resolution, state management, and error handling. Individual nodes implement specific operations through a standardized execution interface.

This separation allows new integrations and node types to be introduced without requiring changes to the underlying execution engine.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | Vue 3, TypeScript |
| Workflow Editor | Vue Flow |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLModel (built on SQLAlchemy + Pydantic) |
| Background Processing | Celery |
| Message Broker | Redis |
| Validation | Pydantic |
| Real-Time Updates | WebSockets |
| Testing | Pytest, Vitest |
| Containerization | Docker |

## Example Use Cases

Pivot is intended to support a broad range of automation scenarios.

**API Automation**
- Periodically retrieve data from external APIs.
- Transform responses into standardized formats.
- Store results in a database.
- Trigger additional operations based on response values.

**Data Processing**
- Ingest structured data from multiple sources.
- Apply transformations and validation.
- Filter records based on configurable conditions.
- Generate reports and persist processed results.

**Notifications and Monitoring**
- Monitor API availability and response times.
- Trigger alerts when predefined conditions are met.
- Send notifications through connected services.
- Track failures and automatically retry operations.

**Scheduled Automation**
- Execute recurring workflows.
- Generate periodic reports.
- Synchronize information between external systems.
- Perform scheduled maintenance and data processing tasks.

**Event-Driven Automation**
- Trigger workflows through incoming webhooks.
- React to changes in external systems.
- Process incoming events asynchronously.
- Execute different operations depending on event data.

## Engineering Goals

The project emphasizes several important software engineering principles:

- **Modularity:** Independently extensible nodes and integrations.
- **Reliability:** Persistent execution state, retry handling, and failure recovery.
- **Scalability:** Asynchronous workers and support for concurrent execution.
- **Observability:** Detailed execution history and node-level monitoring.
- **Type Safety:** Structured input and output validation.
- **Maintainability:** Separation of workflow orchestration, node implementations, and application logic.

## Roadmap

Development is organized around the following milestones.

- [ ] Visual workflow editor and workflow management.
- [ ] Standardized node registry and configuration schemas.
- [ ] Core workflow execution engine.
- [ ] Conditional branching and data propagation.
- [ ] Persistent execution state and execution history.
- [ ] Asynchronous background workers.
- [ ] Scheduled and webhook-based triggers.
- [ ] HTTP and REST API integration.
- [ ] Database integration.
- [ ] Notification integrations.
- [ ] Sports data integration.
- [ ] Real-time execution monitoring.
- [ ] Workflow versioning and execution replay.
- [ ] Automated testing and CI/CD.
- [ ] Docker-based deployment and documentation.

## Project Status

Pivot is an independent open-source project under active development.

The initial focus is establishing a reliable workflow execution engine and a flexible visual editor, followed by an extensible integration ecosystem.

Contributions, feature suggestions, and discussions are welcome.

---

**Pivot**  
*Build workflows. Connect systems. Automate processes.*
