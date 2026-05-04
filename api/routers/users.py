import logging
import os
from typing import Annotated, Any

from dotenv import load_dotenv
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from psycopg import AsyncConnection
from psycopg.errors import UniqueViolation

from ..aws import ses_send_email
from ..db import connect_to_db
from ..schemas.users import (
    RegisterCreds,
    UpdateCreds,
)
from ..utils import log_async_func
from .auth import create_confirmation_token, get_current_user
from ..schemas.base import BaseResponse, ResponseWithId
from ..services.users import register_user, delete_user, update_user

ENV = os.getenv("ENV", "dev")

logger = logging.getLogger(__name__)
load_dotenv(override=True)
router = APIRouter(prefix="/v1/user")


def _send_confirmation_email(email: str, confirmation_url: str) -> None:
    """Send email via AWS SES."""
    message = {
        "Subject": {
            "Data": "[Zapis Stavy] Successfully registered - Please confirm your email",
            "Charset": "UTF-8",
        },
        "Body": {
            "Html": {
                "Data": (
                    "<html>"
                    "<body>"
                    "<p>You were successfully registered into Zapis Stavy app.</p>"
                    "<p></p>"
                    "<p>"
                    f"Please "
                    f"<a href='{confirmation_url}'>confirm your email here</a>"
                    "."
                    "</p>"
                    "</body>"
                    "</html>"
                ),
                "Charset": "UTF-8",
            }
        },
    }
    ses_send_email(email, message)


@router.post("/register", status_code=201, response_model=ResponseWithId)
@log_async_func(logger.info)
async def register_user(
    request: Request,
    user: RegisterCreds,
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    """Add new user into the database.

    Args:
        request: FastAPI request object (used for accessing headers, client info, etc.).
        user: user create request payload from client
        conn: database connection
        background_tasks: FastAPI's background que for tasks

    Returns: response with detail

    Raises:
        HTTPException: if user cannot be inserted in the database
    """
    try:
        registered_user = await register_user(conn, data=user.model_dump())

    except UniqueViolation:
        raise HTTPException(status_code=409, detail="User already exists")

    if registered_user is None:
        raise HTTPException(status_code=500, detail="Registration failed")

    response = {
        "detail": "User registered. Please confirm your email.",
        "id": str(registered_user["id"]),
    }
    confirmation_url = str(
        request.url_for(
            "confirm_user", token=create_confirmation_token(registered_user["id"])
        )
    )
    background_tasks.add_task(
        _send_confirmation_email, registered_user["email"], confirmation_url
    )
    if ENV == "dev":
        response["confirmation_url"] = confirmation_url

    return response


@router.delete("/user", response_model=BaseResponse)
@log_async_func(logger.info)
async def delete_user(
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> dict[str, str]:
    """Delete a user from the database.

    Args:
        conn: database connection
        current_user: current authorized user

    Returns: response with detail
    """
    await delete_user(conn, current_user["id"])
    return {"detail": "User deleted"}


@router.put("/user", response_model=BaseResponse)
@log_async_func(logger.info)
async def update_user(
    user: UpdateCreds,
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> dict[str, str]:
    """Update a meter in the database.

    Args:
        user: user update request payload from client
        conn: database connection
        current_user: current authorized user

    Returns: response with detail

    Raises:
        HTTPException: if user cannot be updated in the database
    """
    await update_user(conn, current_user["id"], data=user.model_dump(exclude_unset=True))
    return {"detail": "User updated"}
