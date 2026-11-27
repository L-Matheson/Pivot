"""Refresh-token cookie helpers."""

from fastapi import Response

from app.core.config import settings


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.cookie_name_refresh,
        value=refresh_token,
        max_age=settings.refresh_token_expire_days * 86400,
        path="/api/auth",
        httponly=True,
        samesite=settings.cookie_samesite,
        secure=settings.cookie_secure,
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.cookie_name_refresh,
        path="/api/auth",
        httponly=True,
        samesite=settings.cookie_samesite,
        secure=settings.cookie_secure,
    )
