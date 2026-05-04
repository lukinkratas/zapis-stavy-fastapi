from pydantic import BaseModel


class BaseResponse(BaseModel):
    """Response json model for validation."""

    detail: str


class ResponseWithId(BaseResponse):
    """Response with id json model for validation."""

    id: str
    confirmation_url: str | None = None