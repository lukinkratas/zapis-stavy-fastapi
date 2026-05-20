import uuid

from pydantic import BaseModel, EmailStr


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


class RegisterCreds(BaseModel):
    """Register user credentials request model for validation."""

    email: EmailStr
    password: str


class UpdateCreds(BaseModel):
    """Update user credentials request model for validation."""

    email: EmailStr | None = None
    password: str | None = None


class CreateProps(BaseModel):
    """Create location properties request model for validation."""

    name: str


class UpdateProps(BaseModel):
    """Update location properties request model for validation."""

    name: str | None = None
