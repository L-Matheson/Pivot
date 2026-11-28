import uuid

from fastapi import HTTPException, status

from app.core.config import settings


def require_encryption_key() -> str:
    if not settings.encryption_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PIVOT_ENCRYPTION_KEY is not configured.",
        )
    return settings.encryption_key


def get_oauth_redirect_uri(provider: str, workspace_id: str | uuid.UUID) -> str:
    base = (
        settings.cors_origins[0]
        if settings.cors_origins
        else "http://localhost:5173"
    )
    return f"{base}/w/{workspace_id}/connections/oauth/{provider}/callback"
