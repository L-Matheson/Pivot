from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PIVOT_", env_file=".env", extra="ignore")

    app_name: str = "Pivot"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173"]

    database_url: PostgresDsn = PostgresDsn("postgresql+psycopg://pivot:pivot@localhost:5432/pivot")
    redis_url: str = "redis://localhost:6379/0"

    # TODO: enforce non-default secret_key in production
    secret_key: str = "change-me-in-production-use-a-random-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7


settings = Settings()
