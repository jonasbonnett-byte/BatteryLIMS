"""Local settings for BatteryLIMS."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_title: str = "BatteryLIMS"
    app_version: str = "0.3.0"
    environment: str = "development"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/batterylims"
    api_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
