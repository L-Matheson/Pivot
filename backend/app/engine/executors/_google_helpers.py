"""Shared Google API helpers for credential lookup and 401-retry."""

from __future__ import annotations

import uuid
from typing import Any

import httpx

from app.connectors import get_connector
from app.connectors.oauth import refresh_access_token
from app.core.encryption import decrypt_credentials, encrypt_credentials
from app.engine.base import ExecutionContext
from app.models.connection import Connection


class CredentialError(Exception):
    pass


def get_google_credentials(
    connection_id: str,
    context: ExecutionContext,
) -> tuple[str, Connection]:
    conn = context.session.get(Connection, uuid.UUID(connection_id))
    if conn is None or conn.workspace_id != context.workspace_id:
        raise CredentialError("Connection not found.")
    if conn.credentials_encrypted is None:
        raise CredentialError("No credentials stored for this connection.")

    creds = decrypt_credentials(conn.credentials_encrypted, context.encryption_key)
    access_token = creds.get("access_token")
    if not access_token:
        raise CredentialError("No access token in stored credentials.")
    return access_token, conn


def _refresh_token(conn: Connection, context: ExecutionContext) -> str:
    creds = decrypt_credentials(conn.credentials_encrypted, context.encryption_key)
    refresh_token_value = creds.get("refresh_token")
    if not refresh_token_value:
        raise CredentialError("No refresh token — re-authorize the connection.")

    connector = get_connector(conn.provider)
    if connector is None or connector.oauth is None:
        raise CredentialError(f"No OAuth config for provider '{conn.provider}'.")

    new_tokens = refresh_access_token(
        token_url=connector.oauth.token_url,
        refresh_token=refresh_token_value,
        client_id=connector.get_client_id(),
        client_secret=connector.get_client_secret(),
    )

    creds["access_token"] = new_tokens["access_token"]
    if "refresh_token" in new_tokens:
        creds["refresh_token"] = new_tokens["refresh_token"]

    conn.credentials_encrypted = encrypt_credentials(creds, context.encryption_key)
    context.session.add(conn)
    context.session.commit()
    return new_tokens["access_token"]


def google_api_request(
    method: str,
    url: str,
    access_token: str,
    body: dict[str, Any] | None,
    connection: Connection,
    context: ExecutionContext,
) -> dict[str, Any]:
    """Make a Google API call with automatic 401-retry using token refresh."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=30) as client:
        if method.upper() == "GET":
            resp = client.get(url, headers=headers)
        else:
            resp = client.post(url, headers=headers, json=body)

    if resp.status_code == 401:
        new_token = _refresh_token(connection, context)
        headers["Authorization"] = f"Bearer {new_token}"
        with httpx.Client(timeout=30) as client:
            if method.upper() == "GET":
                resp = client.get(url, headers=headers)
            else:
                resp = client.post(url, headers=headers, json=body)

    if resp.status_code >= 400:
        raise RuntimeError(
            f"Google API error {resp.status_code}: {resp.text[:500]}"
        )

    return resp.json()
