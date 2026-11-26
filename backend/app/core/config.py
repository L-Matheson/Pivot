from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PIVOT_", env_file=".env", extra="ignore")

    app_name: str = "Pivot"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173"]

    # Database (PostgreSQL via psycopg)
    database_url: PostgresDsn = PostgresDsn("postgresql+psycopg://pivot:pivot@localhost:5432/pivot")

    # Redis (Celery broker / cache — used in later steps)
    redis_url: str = "redis://localhost:6379/0"


settings = Settings()
