import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_title: str = "BatteryLIMS"
    app_version: str = "0.1.0"
    environment: str = "development"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/batterylims"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
