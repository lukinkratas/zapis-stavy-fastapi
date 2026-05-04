from pydantic import BaseModel


class RegisterCreds(BaseModel):
    """User create request model for validation."""

    email: str
    password: str


class UpdateCreds(BaseModel):
    """User update request model for validation."""

    email: str | None = None
    password: str | None = None
