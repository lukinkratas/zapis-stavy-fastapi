"""Routers layer for handling authentication."""

import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from psycopg import AsyncConnection
from psycopg.errors import UniqueViolation

from ..auth import (
    authenticate_user,
    create_access_token,
    create_confirmation_token,
    get_sub,
)
from ..aws import ses_send_email
from ..db import connect_to_db
from ..exceptions import token_exception, user_exists_exception
from ..schemas import BaseResponse, RegisterCreds, ResponseWithId, TokenResponse
from ..services.auth import confirm_user, register_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth")


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


@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_conn: Annotated[AsyncConnection, Depends(connect_to_db)],
) -> TokenResponse:
    """Authenticate user.

    Args:
        form_data: form data with credentials from client
        db_conn: database connection

    Returns: access token

    Raises:
        HTTPException: if user not found in the database or password mismatch.
    """
    user = await authenticate_user(db_conn, form_data.username, form_data.password)
    return TokenResponse(access_token=create_access_token(user.id), token_type="bearer")


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

    return ResponseWithId(
        detail="User registered. Please confirm your email.", id=user.id
    )


@router.get("/confirm/{token}")
async def confirm(
    token: str,
    db_conn: Annotated[AsyncConnection, Depends(connect_to_db)],
) -> BaseResponse:
    """Update user to confirmed = True based on email from token.

    Args:
        token: encoded JWT token
        db_conn: database connection

    Returns: dict with detail message
    """
    user_id = get_sub(token, typ="confirmation")
    user = await confirm_user(db_conn, user_id)

    if user is None:
        raise token_exception

    return BaseResponse(detail="User confirmed")
