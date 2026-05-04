import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from psycopg import AsyncConnection

from ..db import connect_to_db
from ..models.users import users_table
from ..schemas.auth import Token
from ..utils import log_async_func
from ..auth import authenticate_user, create_access_token, get_sub, token_exception

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1")

@router.post("/token", response_model=Token)
@log_async_func(logger.info)
async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
) -> Token:
    """Authenticate user.

    Args:
        form_data: form data with credentials from client
        conn: database connection

    Returns: access token

    Raises:
        HTTPException: if user not found in the database or password mismatch.
    """
    user = await authenticate_user(conn, form_data.username, form_data.password)
    return Token(access_token=create_access_token(user["id"]), token_type="bearer")


@router.get("/confirm/{token}")
@log_async_func(logger.info)
async def confirm_user(
    token: str, conn: Annotated[AsyncConnection, Depends(connect_to_db)]
) -> dict[str, str]:
    """Update user to confirmed = True based on email from token.

    Args:
        token: encoded JWT token
        conn: database connection

    Returns: dict with detail message
    """
    user_id = get_sub(token, typ="confirmation")
    # check user exists
    user = await users_table.select_by_id(conn, user_id)
    if user is None:
        raise token_exception
    await users_table.update(conn, user_id, {"confirmed": True})
    return {"detail": "User confirmed."}
