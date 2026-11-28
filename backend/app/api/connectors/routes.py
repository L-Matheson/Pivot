"""Connector registry API — lists available integration providers."""

from fastapi import APIRouter

from app.connectors import serialize_connectors

router = APIRouter(prefix="/connectors", tags=["connectors"])


@router.get("")
def list_connectors() -> list[dict]:
    return serialize_connectors()
