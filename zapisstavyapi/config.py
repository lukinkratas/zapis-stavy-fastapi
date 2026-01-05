from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Postgres and FastAPI config."""

    # used by both fastapi and docker
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int = 5432

    # used by fast api
    POSTGRES_HOST: str = "localhost"
    ENV_STATE: Literal["dev", "test", "prod"] = "dev"
    LOGTAIL_TOKEN: str
    LOGTAIL_HOST: str

    model_config = SettingsConfigDict(env_file=".env")
