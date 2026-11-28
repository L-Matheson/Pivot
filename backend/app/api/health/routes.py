from fastapi import APIRouter
from sqlalchemy import text

from app.core.db import SessionDep
from app.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health(session: SessionDep) -> HealthResponse:
    try:
        session.exec(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "unavailable"
    return HealthResponse(status="ok", database=db_status)
