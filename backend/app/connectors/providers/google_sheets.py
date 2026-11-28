"""Google Sheets connector — read and write spreadsheet data."""

from app.connectors.base import AuthType, BaseConnector, OAuthConfig
from app.connectors.registry import register
from app.core.config import settings


class GoogleSheetsConnector(BaseConnector):
    slug = "google_sheets"
    display_name = "Google Sheets"
    icon = "sheets"
    auth_type = AuthType.OAUTH2
    description = "Read from and write rows to Google Sheets spreadsheets."

    oauth = OAuthConfig(
        authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        revoke_url="https://oauth2.googleapis.com/revoke",
        scopes=(
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/spreadsheets",
        ),
        extra_authorize_params={"access_type": "offline", "prompt": "consent"},
    )

    triggers = ()
    actions = ("write_spreadsheet",)

    def get_client_id(self) -> str:
        return settings.google_client_id

    def get_client_secret(self) -> str:
        return settings.google_client_secret


register(GoogleSheetsConnector())
