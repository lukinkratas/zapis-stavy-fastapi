import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Literal

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from psycopg import AsyncConnection

from .config import get_jwt_settings
from .db import connect_to_db
from .exceptions import credentials_exception, token_exception
from .repositories.users import UserRow
from .security import verify_password
from .services.users import select_user_by_email, select_user_by_id
from .utils import log_async_func, log_func
from .config import JwtSettings

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token")


@log_async_func(logger.debug)
async def authenticate_user(
    db_conn: AsyncConnection, email: str, password: str
) -> dict[str, Any]:
    """Authenticate user.

    Args:
        db_conn: database connection
        email: email to authenticate
        password: password corresponding to the email

    Returns: user dict

    Raises:
        HTTPException: if user is not found in the database or password mismatch.
    """
    user = await select_user_by_email(db_conn, email)

    if user is None or not verify_password(password, user.password_hash):
        raise credentials_exception

    return user


def _create_jwt_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    """Create JWT token.

    Args:
        data: data to be encoded
        expires_delta: expire period of token

    Returns: encoded JWT token
    """
    jwt_settings = get_jwt_settings()
    expire = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(
        data | {"exp": expire},
        key=jwt_settings.secret_key,
        algorithm=jwt_settings.algorithm,
    )


@log_func(logger.debug)
def create_access_token(
    user_id: uuid.UUID, expires_delta: timedelta = timedelta(minutes=15)
) -> str:
    """Create access token.

    Args:
        user_id: user id to be encoded
        expires_delta: expire period of token

    Returns: encoded JWT token
    """
    return _create_jwt_token({"type": "access", "sub": str(user_id)}, expires_delta)


@log_func(logger.debug)
def create_confirmation_token(
    user_id: uuid.UUID, expires_delta: timedelta = timedelta(hours=24)
) -> str:
    """Create confirmation token.

    Args:
        user_id: user id to be encoded
        expires_delta: expire period of token

    Returns: encoded JWT token
    """
    return _create_jwt_token(
        {"type": "confirmation", "sub": str(user_id)}, expires_delta
    )


def _get_sub(token: str, typ: Literal["access", "confirmation"]) -> str:
    """Get subject from JWT token.

    Args:
        token: encoded JWT token
        typ: token type, either access or confirmation

    Returns: decoded user id
    """
    jwt_settings = get_jwt_settings()
    try:
        payload = jwt.decode(
            token, key=jwt_settings.secret_key, algorithms=[jwt_settings.algorithm]
        )

    except InvalidTokenError as e:
        raise token_exception from e

    user_id = payload.get("sub")

    if user_id is None or payload.get("type") != typ:
        raise token_exception

    return user_id


@log_async_func(logger.debug)
async def get_current_user(
    db_conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> UserRow:
    """Get current user from token.

    Args:
        db_conn: database connection
        token: JWT token with encoded email

    Returns: user row

    Raises:
        HTTPException: if user is not found in the database.
    """
    user_id = _get_sub(token, typ="access")
    user = await select_user_by_id(db_conn, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@log_async_func(logger.debug)
async def get_current_confirmed_user(
    current_user: Annotated[UserRow, Depends(get_current_user)],
) -> UserRow:
    """Get current user from token.

    Args:
        current_user: current authorized user

    Returns: user row

    Raises:
        HTTPException: if user is not confirmed.
    """
    if current_user.confirmed is not True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not confirmed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return current_user
