import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from psycopg import AsyncConnection
from pwdlib import PasswordHash
from dotenv import load_dotenv

from ..config import settings
from ..db import connect_to_db
from ..models.users import users_table
from ..schemas.auth import Token
from ..utils import log_async_func, log_func
from ..auth import authenticate_user, create_access_token

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
