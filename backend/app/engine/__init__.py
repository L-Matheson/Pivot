"""Workflow execution engine — public API."""

import app.engine.executors  # noqa: F401 — triggers self-registration
from app.engine.registry import get_executor, register_executor
from app.engine.runner import run_workflow

__all__ = ["get_executor", "register_executor", "run_workflow"]
