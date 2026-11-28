"""Google Gmail connector — read emails, send email via Gmail API."""

from app.connectors.base import AuthType, BaseConnector, OAuthConfig
from app.connectors.registry import register
from app.core.config import settings


class GoogleGmailConnector(BaseConnector):
    slug = "google_gmail"
    display_name = "Gmail"
    icon = "gmail"
    auth_type = AuthType.OAUTH2
    description = "Read and send email through a connected Gmail account."

    oauth = OAuthConfig(
        authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        revoke_url="https://oauth2.googleapis.com/revoke",
        scopes=(
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.labels",
            "https://www.googleapis.com/auth/gmail.send",
        ),
        extra_authorize_params={"access_type": "offline", "prompt": "consent"},
    )

    triggers = ("email_trigger",)
    actions = ("send_email",)

    def get_client_id(self) -> str:
        return settings.google_client_id

    def get_client_secret(self) -> str:
        return settings.google_client_secret


register(GoogleGmailConnector())
