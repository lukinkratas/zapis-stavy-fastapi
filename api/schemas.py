import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class BaseResponse(BaseModel):
    """Response json model for validation."""

    detail: str


class ResponseWithId(BaseResponse):
    """Response with id json model for validation."""

    id: uuid.UUID


class TokenResponse(BaseModel):
    """Response token model for validation."""

    access_token: str
    token_type: str


class Location(BaseModel):
    """Location row database model."""

    id: uuid.UUID
    created_at: datetime
    user_id: uuid.UUID
    location_name: str


class LocationsResponse(BaseModel):
    """Response token model for validation."""

    locations: list[Location]


class RegisterUserCredentials(BaseModel):
    """Register user credentials request model for validation."""

    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str


class UpdateUserCredentials(BaseModel):
    """Update user credentials request model for validation."""

    model_config = ConfigDict(extra="forbid")
    email: EmailStr | None = None
    password: str | None = None


class CreateLocationProperties(BaseModel):
    """Create location properties request model for validation."""

    model_config = ConfigDict(extra="forbid")
    location_name: str


class UpdateLocationProperties(BaseModel):
    """Update location properties request model for validation."""

    model_config = ConfigDict(extra="forbid")
    location_name: str | None = None
