import uuid

from pydantic import BaseModel


class BaseResponse(BaseModel):
    """Response json model for validation."""

    detail: str


class ResponseWithId(BaseResponse):
    """Response with id json model for validation."""

    id: uuid.UUID
    confirmation_token: str | None = None


class RegisterCreds(BaseModel):
    """User create request model for validation."""

    email: str
    password: str


class UpdateCreds(BaseModel):
    """User update request model for validation."""

    email: str | None = None
    password: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class LocationCreateRequest(BaseModel):
    """Location create request model for validation."""

    name: str


class LocationUpdateRequest(BaseModel):
    """Location update request model for validation."""

    name: str | None = None
