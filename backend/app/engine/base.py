"""Execution engine base types.

All node executors depend on these types. Nothing here imports FastAPI
so the engine can run from background workers later.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

from sqlmodel import Session


@dataclass(slots=True)
class NodeResult:
    node_id: str
    status: Literal["completed", "failed", "skipped"]
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    duration_ms: int = 0


@dataclass(slots=True)
class ExecutionContext:
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    session: Session
    encryption_key: str


@dataclass(slots=True)
class WorkflowRunResult:
    execution_id: uuid.UUID
    status: Literal["completed", "failed"]
    node_results: list[NodeResult]
    started_at: datetime
    finished_at: datetime


class BaseNodeExecutor(ABC):
    @abstractmethod
    def execute(
        self,
        node_id: str,
        config: dict[str, Any],
        inputs: dict[str, Any],
        context: ExecutionContext,
    ) -> NodeResult: ...
