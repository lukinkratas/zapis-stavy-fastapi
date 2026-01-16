import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from psycopg import AsyncConnection
from pwdlib import PasswordHash

from ..config import settings
from ..db import connect_to_db
from ..db_models.users import users_table
from ..models.auth import Token
from ..utils import log_async_func, log_func

logger = logging.getLogger(__name__)
router = APIRouter()

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentisl",
    headers={"WWW-Authenticate": "Bearer"},
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare password and password hash.

    Args:
        plain_password: textual form of password
        hashed_password: password hash

    Returns: True if passwords match, otherwise False
    """
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Get hashed password.

    Args:
        password: textual form of password

    Returns: hashed password
    """
    return password_hash.hash(password)


@log_async_func(logger.info)
async def get_user(conn: AsyncConnection, email: str) -> dict[str, Any]:
    """Get user from the database.

    Args:
        conn: database connection
        email: email of the user

    Returns: user dict
    """
    return await users_table.select_by_email(conn, email)


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
        HTTPException: if user not found in database or password mismatch.
    """
    logger.debug("Authenticating user", extra={"email": email})
    user = await get_user(conn, email)

    if not user or not verify_password(password, user["password"]):
        raise credentials_exception

    return user


@log_func(logger.info)
def create_access_token(email: str) -> str:
    """Create access token.

    Args:
        email: email to be encoded

    Return: encoded JWT token
    """
    logger.debug("Created access token", extra={"email": email})
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    data = {"sub": email, "exp": expire}
    return jwt.encode(data, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)


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
    """
    try:
        payload = jwt.decode(
            token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    user = await get_user(conn, email=email)

    if not user:
        raise credentials_exception

    return user


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
    """
    user = await authenticate_user(conn, form_data.username, form_data.password)
    return Token(access_token=create_access_token(user["email"]), token_type="bearer")
