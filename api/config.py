from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Postgres and FastAPI config."""

    DB_NAME: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_PORT: int = 5432
    DB_HOST: str = "localhost"
    LOGTAIL_TOKEN: str | None = None
    LOGTAIL_HOST: str | None = None
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
