import logging
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from psycopg import AsyncConnection
from psycopg.errors import UniqueViolation

from ..aws import ses_send_email
from ..db import connect_to_db
from ..models.users import users_table
from ..schemas.users import (
    UserCreateRequestBody,
    UserResponseJson,
    UserUpdateRequestBody,
)
from ..utils import log_async_func
from .auth import create_confirmation_token, get_current_user, get_password_hash

logger = logging.getLogger(__name__)
router = APIRouter()


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


@router.post("/register", status_code=201)
@log_async_func(logger.info)
async def register_user(
    request: Request,
    user: UserCreateRequestBody,
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    background_tasks: BackgroundTasks,
) -> dict[str, Any]:
    """Add new user into the database.

    Args:
        request: FastAPI request object (used for accessing headers, client info, etc.).
        user: user create request payload from client
        conn: database connection
        background_tasks: FastAPI's background que for tasks

    Returns: user dict

    Raises:
        HTTPException: if user cannot be inserted in the database
    """
    data = user.model_dump()
    data["password"] = get_password_hash(user.password)

    try:
        registered_user = await users_table.insert(conn, data)

    except UniqueViolation:
        raise HTTPException(status_code=409, detail="User already exists.")

    if registered_user is None:
        raise HTTPException(status_code=500, detail="User registration failed.")

    confirmation_url = str(
        request.url_for(
            "confirm", token=create_confirmation_token(registered_user["id"])
        )
    )
    background_tasks.add_task(
        _send_confirmation_email, registered_user["email"], confirmation_url
    )
    return {
        "detail": "User registered. Please confirm your email.",
        "user": registered_user,
        "confirmation_url": confirmation_url,  # TODO: remove
    }


@router.delete("/user", status_code=200)
@log_async_func(logger.info)
async def delete_user(
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> None:
    """Delete a user from the database.

    Args:
        conn: database connection
        current_user: current authorized user

    Returns: None

    Raises:
        HTTPException: if user cannot be deleted from the database
    """
    await users_table.delete(conn, current_user["id"])


@router.put("/user", response_model=UserResponseJson)
@log_async_func(logger.info)
async def update_user(
    user: UserUpdateRequestBody,
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> dict[str, Any]:
    """Update a meter in the database.

    Args:
        user: user update request payload from client
        conn: database connection
        current_user: current authorized user

    Returns: meter dict

    Raises:
        HTTPException: if user cannot be updated in the database
    """
    data = user.model_dump()
    if data.get("password") is not None:
        data["password"] = get_password_hash(user.password)  # type: ignore[arg-type]

    updated_user = await users_table.update(conn, current_user["id"], data)

    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return updated_user
