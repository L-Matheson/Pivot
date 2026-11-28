"""Connector registry — discovers and stores all provider instances.

Providers register themselves by calling ``register()`` at module level.
The ``providers/__init__.py`` module auto-imports every provider file so
registration happens at first import of this package.
"""

from __future__ import annotations

from app.connectors.base import BaseConnector

_CONNECTORS: dict[str, BaseConnector] = {}


def register(connector: BaseConnector) -> None:
    _CONNECTORS[connector.slug] = connector


def get_connector(slug: str) -> BaseConnector | None:
    return _CONNECTORS.get(slug)


def list_connectors() -> list[BaseConnector]:
    return list(_CONNECTORS.values())


def serialize_connectors() -> list[dict]:
    return [c.serialize() for c in _CONNECTORS.values()]
