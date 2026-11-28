"""Base connector class and shared types.

Every connector subclasses BaseConnector and is auto-registered when its
module is imported.  Adding a new provider = one file in providers/.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum


class AuthType(StrEnum):
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    CONNECTION_STRING = "connection_string"


@dataclass(frozen=True, slots=True)
class OAuthConfig:
    authorization_url: str
    token_url: str
    scopes: tuple[str, ...]
    revoke_url: str = ""
    extra_authorize_params: dict[str, str] | None = None


class BaseConnector(ABC):
    """Strategy interface that every provider implements."""

    @property
    @abstractmethod
    def slug(self) -> str: ...

    @property
    @abstractmethod
    def display_name(self) -> str: ...

    @property
    @abstractmethod
    def icon(self) -> str: ...

    @property
    @abstractmethod
    def auth_type(self) -> AuthType: ...

    @property
    def oauth(self) -> OAuthConfig | None:
        return None

    @property
    def triggers(self) -> tuple[str, ...]:
        return ()

    @property
    def actions(self) -> tuple[str, ...]:
        return ()

    @property
    def description(self) -> str:
        return ""

    def get_client_id(self) -> str:
        return ""

    def get_client_secret(self) -> str:
        return ""

    def serialize(self) -> dict:
        entry: dict = {
            "slug": self.slug,
            "display_name": self.display_name,
            "icon": self.icon,
            "auth_type": self.auth_type,
            "description": self.description,
            "triggers": list(self.triggers),
            "actions": list(self.actions),
        }
        if self.oauth:
            entry["scopes"] = list(self.oauth.scopes)
        return entry
