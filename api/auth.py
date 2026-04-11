import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from psycopg import AsyncConnection
from pwdlib import PasswordHash

from .db import connect_to_db
from .models.users import users_table
from .utils import log_async_func, log_func

load_dotenv(override=True)
logger = logging.getLogger(__name__)
router = APIRouter()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.getenv("ALGORITHM", "HS256")

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_password_hash(password: str) -> str:
    """Get hashed password.

    Args:
        password: textual form of password

    Returns: hashed password
    """
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare password and password hash.

    Args:
        plain_password: textual form of password
        hashed_password: password hash

    Returns: True if passwords match, otherwise False
    """
    return password_hash.verify(plain_password, hashed_password)


@log_async_func(logger.info)
async def get_user(conn: AsyncConnection, email: str) -> dict[str, Any]:
    """Get user from the database.

    Args:
        conn: database connection
        email: email of the user

    Returns: user dict

    Raises:
        HTTPException: if user is not found in the database.
    """
    user = await users_table.select_by_email(conn, email)

    if user is None:
        raise credentials_exception

    return user


@log_async_func(logger.info)
async def authenticate_user(
    conn: AsyncConnection, email: str, password: str
) -> dict[str, Any]:
    """Authenticate user.

    Args:
        conn: database connection
        email: email to authenticate
        password: password corresponding to the email

    Returns: user dict

    Raises:
        HTTPException: if user not found in the database or password mismatch.
    """
    logger.debug("Authenticating user", extra={"email": email})
    user = await get_user(conn, email)

    if not verify_password(password, user["password"]):
        raise credentials_exception

    return user


@log_func(logger.info)
def create_jwt_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    """Create JWT token.

    Args:
        data: data to be encoded
        expires_delta: expire period of token

    Return: encoded JWT token
    """
    expire = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(data | {"exp": expire}, key=SECRET_KEY, algorithm=ALGORITHM)


@log_func(logger.info)
def create_confirmation_token(email: str) -> str:
    """Create confirmation token.

    Args:
        email: email to be encoded

    Return: encoded JWT token
    """
    return create_jwt_token({"type": "confirmation", "sub": email}, timedelta(hours=24))


@log_func(logger.info)
def create_access_token(email: str) -> str:
    """Create access token.

    Args:
        email: email to be encoded

    Return: encoded JWT token
    """
    return create_jwt_token({"type": "access", "sub": email}, timedelta(minutes=15))


@log_async_func(logger.info)
async def get_current_user(
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> dict[str, Any]:
    """Get current user from token.

    Args:
        conn: database connection
        token: JWT token with encoded email

    Returns: user dict

    Raises:
        HTTPException: if token is not valid or user is not found in the database.
    """
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

    except InvalidTokenError as e:
        raise credentials_exception from e

    return await get_user(conn, email)
