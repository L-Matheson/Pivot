from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from app.core.db import SessionDep

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    status: str
    database: str


@router.get("")
def health(session: SessionDep) -> HealthResponse:
    """Return service health including a database connectivity check."""
    try:
        session.exec(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "unavailable"
    return HealthResponse(status="ok", database=db_status)
