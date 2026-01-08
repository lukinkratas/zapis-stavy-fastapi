import datetime
import uuid

from pydantic import BaseModel


class UserCreateRequestBody(BaseModel):
    """User response json model for validation."""

    email: str
    password: str


class UserResponseJson(BaseModel):
    """User response json model for validation."""

    id: uuid.UUID
    created_at: datetime.datetime
    email: str
