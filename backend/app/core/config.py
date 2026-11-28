from __future__ import annotations

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic import PostgresDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_SECRET = "change-me-in-production-use-a-random-secret"


def _generate_rsa_keypair() -> tuple[str, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_pem, public_pem


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PIVOT_", env_file=".env", extra="forbid")

    app_name: str = "Pivot"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173"]

    database_url: PostgresDsn = PostgresDsn("postgresql+psycopg://pivot:pivot@localhost:5432/pivot")
    redis_url: str = "redis://localhost:6379/0"

    secret_key: str = _DEFAULT_SECRET
    jwt_algorithm: str = "RS256"
    jwt_private_key: str = ""
    jwt_public_key: str = ""
    jwt_issuer: str = "pivot"
    jwt_audience: str = "pivot"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    cookie_name_refresh: str = "pivot_refresh"

    encryption_key: str = ""

    google_client_id: str = ""
    google_client_secret: str = ""

    @model_validator(mode="after")
    def _validate_secrets(self) -> Settings:
        if not self.debug and self.secret_key == _DEFAULT_SECRET:
            raise ValueError(
                "PIVOT_SECRET_KEY must be set to a unique random value when "
                "PIVOT_DEBUG is not true."
            )

        if self.jwt_algorithm == "RS256" and not self.jwt_private_key:
            if self.debug:
                self.jwt_private_key, self.jwt_public_key = _generate_rsa_keypair()
            else:
                raise ValueError(
                    "PIVOT_JWT_PRIVATE_KEY must be set when using RS256 and "
                    "PIVOT_DEBUG is not true."
                )

        if self.jwt_private_key and not self.jwt_public_key:
            private_key = serialization.load_pem_private_key(
                self.jwt_private_key.encode(), password=None,
            )
            self.jwt_public_key = private_key.public_key().public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode()

        return self

    @property
    def jwt_signing_key(self) -> str:
        if self.jwt_algorithm == "RS256":
            return self.jwt_private_key
        return self.secret_key

    @property
    def jwt_verifying_key(self) -> str:
        if self.jwt_algorithm == "RS256":
            return self.jwt_public_key
        return self.secret_key


settings = Settings()
