"""Routers layer for handling users lifecycle - register, update and delete.

Pydantic validation is handled in this module.
Database connection is passed to downstream user service.
"""

import logging
import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from psycopg import AsyncConnection
from psycopg.errors import UniqueViolation

from ..auth import create_confirmation_token, get_current_user
from ..aws import ses_send_email
from ..db import connect_to_db
from ..exceptions import user_exists_exception, user_not_found_exception
from ..repositories.users import UserRow
from ..schemas import BaseResponse, RegisterCreds, ResponseWithId, UpdateCreds
from ..services.users import delete_user, register_user, update_user

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
                    "Please "
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
async def register(
    request: Request,
    creds: RegisterCreds,
    db_conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    background_tasks: BackgroundTasks,
) -> ResponseWithId:
    """Register new user.

    Args:
        request: FastAPI request object (used for accessing headers, client info, etc.).
        creds: register credentials payload from client
        db_conn: database connection
        background_tasks: FastAPI's background que for tasks

    Returns: response with detail and user_id

    Raises:
        HTTPException: if user already exists
    """
    try:
        user = await register_user(db_conn, creds)

    except UniqueViolation:
        raise user_exists_exception

    confirmation_token = create_confirmation_token(user.id)
    logger.debug(f"{confirmation_token=}")
    background_tasks.add_task(
        _send_confirmation_email,
        user.email,
        confirmation_url=str(request.url_for("confirm", token=confirmation_token)),
    )

    return ResponseWithId(detail="User registered. Please confirm your email.", id=user.id)


@router.put("")
async def update(
    creds: UpdateCreds,
    db_conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_user: Annotated[UserRow, Depends(get_current_user)],
) -> BaseResponse:
    """Update a user.

    Args:
        creds: credentials update payload from client
        db_conn: database connection
        current_user: current authorized user

    Returns: response with detail

    Raises:
        HTTPException: if user was not found or email already exists.
    """
    try:
        user = await update_user(db_conn, current_user.id, creds)

        if not user:
            raise user_not_found_exception

    except UniqueViolation:
        raise HTTPException(status_code=409, detail="Email already in use")

    return BaseResponse(detail="User updated")


@router.delete("")
async def delete(
    db_conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_user: Annotated[UserRow, Depends(get_current_user)],
) -> BaseResponse:
    """Delete a user.

    Args:
        db_conn: database connection
        current_user: current authorized user

    Returns: response with detail

    Raises:
        HTTPException: if user was not found
    """
    user = await delete_user(db_conn, current_user.id)

    if not user:
        raise user_not_found_exception

    return BaseResponse(detail="User deleted")
