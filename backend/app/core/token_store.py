"""Server-side refresh token store backed by Redis.

Each refresh token carries a unique ``jti`` claim. On login and refresh,
the jti is stored in Redis with a TTL matching the token's lifetime.
On refresh or logout, the old jti is deleted, revoking the token
immediately, even if it hasn't expired yet.
"""

from __future__ import annotations

import redis

from app.core.config import settings

_pool: redis.ConnectionPool | None = None


def _get_client() -> redis.Redis:
    global _pool
    if _pool is None:
        _pool = redis.ConnectionPool.from_url(settings.redis_url, decode_responses=True)
    return redis.Redis(connection_pool=_pool)


def _key(jti: str) -> str:
    return f"refresh:{jti}"


def store_refresh_token(jti: str, user_id: str) -> None:
    ttl = settings.refresh_token_expire_days * 86400
    _get_client().setex(_key(jti), ttl, user_id)


def is_refresh_token_valid(jti: str) -> bool:
    return _get_client().exists(_key(jti)) == 1


def revoke_refresh_token(jti: str) -> None:
    _get_client().delete(_key(jti))


def revoke_all_user_tokens(user_id: str) -> None:
    """Revoke all refresh tokens for a user. Uses SCAN to avoid blocking."""
    client = _get_client()
    cursor = 0
    while True:
        cursor, keys = client.scan(cursor, match="refresh:*", count=100)
        for key in keys:
            if client.get(key) == user_id:
                client.delete(key)
        if cursor == 0:
            break
