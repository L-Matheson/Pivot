"""Node executor registry — maps node type slugs to executor instances."""

from __future__ import annotations

from app.engine.base import BaseNodeExecutor

_EXECUTORS: dict[str, BaseNodeExecutor] = {}


def register_executor(slug: str, executor: BaseNodeExecutor) -> None:
    _EXECUTORS[slug] = executor


def get_executor(slug: str) -> BaseNodeExecutor | None:
    return _EXECUTORS.get(slug)
