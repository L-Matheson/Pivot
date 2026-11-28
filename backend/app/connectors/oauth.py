"""OAuth2 token exchange and refresh helpers.

Extracted from the API layer so connectors and background workers can
reuse the same logic without importing FastAPI.
"""

import httpx


class OAuthError(Exception):
    def __init__(self, detail: str, status_code: int = 502):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


def exchange_code_for_tokens(
    token_url: str,
    code: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
) -> dict:
    with httpx.Client(timeout=30) as client:
        resp = client.post(
            token_url,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if resp.status_code != 200:
        raise OAuthError(f"Token exchange failed: {resp.text}")
    return resp.json()


def refresh_access_token(
    token_url: str,
    refresh_token: str,
    client_id: str,
    client_secret: str,
) -> dict:
    with httpx.Client(timeout=30) as client:
        resp = client.post(
            token_url,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if resp.status_code != 200:
        raise OAuthError(f"Token refresh failed: {resp.text}")
    return resp.json()
