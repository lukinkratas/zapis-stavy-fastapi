from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings."""

    env: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class DbSettings(BaseSettings):
    """Database settings."""

    name: str
    username: str
    password: str
    host: str = "postgres"
    port: int = 5432

    model_config = SettingsConfigDict(env_file=".env", env_prefix="DB_", extra="ignore")


class JwtSettings(BaseSettings):
    """Auth settings."""

    secret_key: str
    algorithm: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="JWT_", extra="ignore"
    )


class AwsSettings(BaseSettings):
    """AWS settings."""

    access_key_id: str
    secret_access_key: str
    region_name: str

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="AWS_", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """Lazy init app settings."""
    return Settings()


@lru_cache
def get_db_settings() -> DbSettings:
    """Lazy init database settings."""
    return DbSettings()


@lru_cache
def get_jwt_settings() -> JwtSettings:
    """Lazy init auth settings."""
    return JwtSettings()


@lru_cache
def get_aws_settings() -> AwsSettings:
    """Lazy init aws settings."""
    return AwsSettings()
