from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class JwtSettings(BaseSettings):
    """Settings for auth."""

    secret_key: str
    algorithm: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="JWT_", extra="ignore"
    )


@lru_cache
def get_jwt_settings() -> JwtSettings:
    """Lazy init settings for auth."""
    return JwtSettings()
