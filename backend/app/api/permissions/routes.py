"""Permission catalog endpoint — exposes the canonical resource/action list."""

from typing import Any

from fastapi import APIRouter

from app.core.permission_registry import serialize

router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.get("")
def list_permissions() -> list[dict[str, Any]]:
    return serialize()
