from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PIVOT_", env_file=".env", extra="ignore")

    app_name: str = "Pivot"
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
