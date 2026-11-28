"""OAuth2 authorization flow routes for connections."""

import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.connectors import get_connector
from app.connectors.oauth import OAuthError, exchange_code_for_tokens, refresh_access_token
from app.core.auth import CurrentUserDep, PermissionRequired
from app.core.db import SessionDep
from app.core.encryption import decrypt_credentials, encrypt_credentials
from app.models.base import utc_now
from app.models.connection import Connection
from app.schemas.connection import (
    ConnectionRead,
    OAuthAuthorizeResponse,
    OAuthCallbackRequest,
)

from .commands import get_workspace_connection
from .utils import get_oauth_redirect_uri, require_encryption_key

router = APIRouter(prefix="/workspaces/{workspace_id}/connections", tags=["connections"])

_pending_oauth_states: dict[str, dict] = {}


@router.get(
    "/oauth/{provider}/authorize",
    response_model=OAuthAuthorizeResponse,
    dependencies=[Depends(PermissionRequired("connections", "manage"))],
)
def oauth_authorize(
    workspace_id: uuid.UUID,
    provider: str,
    user: CurrentUserDep,
) -> dict:
    connector = get_connector(provider)
    if connector is None or connector.oauth is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider '{provider}' does not support OAuth2.",
        )

    client_id = connector.get_client_id()
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth client ID not configured for '{provider}'.",
        )

    state = secrets.token_urlsafe(32)
    _pending_oauth_states[state] = {
        "provider": provider,
        "workspace_id": str(workspace_id),
        "user_id": str(user.id),
    }

    redirect_uri = get_oauth_redirect_uri(provider, workspace_id)
    scopes = " ".join(connector.oauth.scopes)

    params = (
        f"client_id={client_id}&redirect_uri={redirect_uri}"
        f"&response_type=code&scope={scopes}&state={state}"
    )
    if connector.oauth.extra_authorize_params:
        for k, v in connector.oauth.extra_authorize_params.items():
            params += f"&{k}={v}"

    authorize_url = f"{connector.oauth.authorization_url}?{params}"
    return {"authorize_url": authorize_url, "state": state}


@router.post(
    "/oauth/{provider}/callback",
    response_model=ConnectionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionRequired("connections", "manage"))],
)
def oauth_callback(
    workspace_id: uuid.UUID,
    provider: str,
    body: OAuthCallbackRequest,
    session: SessionDep,
    user: CurrentUserDep,
) -> Connection:
    pending = _pending_oauth_states.pop(body.state, None)
    if pending is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OAuth state.",
        )

    if pending["provider"] != provider or pending["workspace_id"] != str(workspace_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth state mismatch.",
        )

    connector = get_connector(provider)
    if connector is None or connector.oauth is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider '{provider}' does not support OAuth2.",
        )

    redirect_uri = get_oauth_redirect_uri(provider, workspace_id)

    try:
        token_data = exchange_code_for_tokens(
            token_url=connector.oauth.token_url,
            code=body.code,
            client_id=connector.get_client_id(),
            client_secret=connector.get_client_secret(),
            redirect_uri=redirect_uri,
        )
    except OAuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from None

    key = require_encryption_key()
    encrypted = encrypt_credentials(token_data, key)

    connection = Connection(
        workspace_id=workspace_id,
        provider=provider,
        name=f"{connector.display_name} ({user.email})",
        auth_type="oauth2",
        credentials_encrypted=encrypted,
        scopes=" ".join(connector.oauth.scopes),
        status="connected",
        connected_by_user_id=user.id,
    )
    session.add(connection)
    session.commit()
    session.refresh(connection)
    return connection


@router.post(
    "/{connection_id}/refresh",
    response_model=ConnectionRead,
    dependencies=[Depends(PermissionRequired("connections", "manage"))],
)
def refresh_oauth_token(
    workspace_id: uuid.UUID,
    connection_id: uuid.UUID,
    session: SessionDep,
) -> Connection:
    conn = get_workspace_connection(session, workspace_id, connection_id)
    if conn.auth_type != "oauth2":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connection is not OAuth2.",
        )

    key = require_encryption_key()
    creds = decrypt_credentials(conn.credentials_encrypted, key)

    refresh_token_value = creds.get("refresh_token")
    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No refresh token stored. Re-authorize the connection.",
        )

    connector = get_connector(conn.provider)
    if connector is None or connector.oauth is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provider OAuth config not found.",
        )

    try:
        new_tokens = refresh_access_token(
            token_url=connector.oauth.token_url,
            refresh_token=refresh_token_value,
            client_id=connector.get_client_id(),
            client_secret=connector.get_client_secret(),
        )
    except OAuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from None

    creds["access_token"] = new_tokens["access_token"]
    if "refresh_token" in new_tokens:
        creds["refresh_token"] = new_tokens["refresh_token"]
    if "expires_in" in new_tokens:
        creds["expires_in"] = new_tokens["expires_in"]

    conn.credentials_encrypted = encrypt_credentials(creds, key)
    conn.status = "connected"
    conn.updated_at = utc_now()
    session.add(conn)
    session.commit()
    session.refresh(conn)
    return conn
