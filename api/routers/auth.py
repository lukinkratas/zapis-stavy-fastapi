"""Routers layer for handling authentication."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from psycopg import AsyncConnection

from ..auth import _get_sub, authenticate_user, create_access_token
from ..db import connect_to_db
from ..exceptions import token_exception
from ..schemas import Token
from ..services.auth import confirm_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/auth")


@router.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_conn: Annotated[AsyncConnection, Depends(connect_to_db)],
) -> Token:
    """Authenticate user.

    Args:
        form_data: form data with credentials from client
        db_conn: database connection

    Returns: access token

    Raises:
        HTTPException: if user not found in the database or password mismatch.
    """
    user = await authenticate_user(db_conn, form_data.username, form_data.password)
    return Token(access_token=create_access_token(user.id), token_type="bearer")


@router.get("/confirm/{token}")
async def confirm(
    token: str,
    db_conn: Annotated[AsyncConnection, Depends(connect_to_db)],
) -> dict[str, str]:
    """Update user to confirmed = True based on email from token.

    Args:
        token: encoded JWT token
        db_conn: database connection

    Returns: dict with detail message
    """
    user_id = _get_sub(token, typ="confirmation")
    user = await confirm_user(db_conn, user_id)

    if user is None:
        raise token_exception

    return {"detail": "User confirmed."}
