from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Postgres and FastAPI config."""

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int = 5432
    POSTGRES_HOST: str = "localhost"
    ENV: Literal["dev", "test", "prod"] = "dev"
    LOGTAIL_TOKEN: str | None = None
    LOGTAIL_HOST: str | None = None
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
