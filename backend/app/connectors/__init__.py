"""Connector package — public API.

Importing this package triggers provider auto-discovery so all
connectors are registered before any lookup.
"""

import app.connectors.providers  # noqa: F401 — triggers self-registration
from app.connectors.registry import get_connector, list_connectors, serialize_connectors

__all__ = ["get_connector", "list_connectors", "serialize_connectors"]
