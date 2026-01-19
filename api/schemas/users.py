import datetime
import uuid

from pydantic import BaseModel


class UserCreateRequestBody(BaseModel):
    """User create response json model for validation."""

    email: str
    password: str


class UserUpdateRequestBody(BaseModel):
    """User update response json model for validation."""

    email: str | None = None
    password: str | None = None


class UserResponseJson(BaseModel):
    """User response json model for validation."""

    id: uuid.UUID
    created_at: datetime.datetime
    email: str
    password: str
