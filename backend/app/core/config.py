from pydantic import PostgresDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_SECRET = "change-me-in-production-use-a-random-secret"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PIVOT_", env_file=".env", extra="forbid")

    app_name: str = "Pivot"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173"]

    database_url: PostgresDsn = PostgresDsn("postgresql+psycopg://pivot:pivot@localhost:5432/pivot")
    redis_url: str = "redis://localhost:6379/0"

    secret_key: str = _DEFAULT_SECRET
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "pivot"
    jwt_audience: str = "pivot"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    @model_validator(mode="after")
    def _reject_default_secret_in_production(self) -> "Settings":
        if not self.debug and self.secret_key == _DEFAULT_SECRET:
            raise ValueError(
                "PIVOT_SECRET_KEY must be set to a unique random value when "
                "PIVOT_DEBUG is not true."
            )
        return self


settings = Settings()
