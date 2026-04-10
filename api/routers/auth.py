import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from psycopg import AsyncConnection

from ..auth import authenticate_user, create_access_token
from ..db import connect_to_db
from ..schemas.auth import Token
from ..utils import log_async_func

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/token", response_model=Token)
@log_async_func(logger.info)
async def login(
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
    return Token(access_token=create_access_token(user["email"]), token_type="bearer")
