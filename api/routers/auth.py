import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Literal

import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from psycopg import AsyncConnection
from pwdlib import PasswordHash

from ..db import connect_to_db
from ..models.users import users_table
from ..schemas.auth import Token
from ..utils import log_async_func, log_func

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

token_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token",
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
        HTTPException: if user is not found in the database or password mismatch.
    """
    user = await get_user(conn, email)

    if user is None:
        raise credentials_exception

    if not verify_password(password, user["password"]):
        raise credentials_exception

    return user


@log_func(logger.info)
def _create_jwt_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    """Create JWT token.

    Args:
        data: data to be encoded
        expires_delta: expire period of token

    Returns: encoded JWT token
    """
    expire = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(data | {"exp": expire}, key=SECRET_KEY, algorithm=ALGORITHM)


@log_func(logger.info)
def create_access_token(email: str) -> str:
    """Create access token.

    Args:
        email: email to be encoded

    Returns: encoded JWT token
    """
    return _create_jwt_token({"type": "access", "sub": email}, timedelta(minutes=15))


@log_func(logger.info)
def create_confirmation_token(email: str) -> str:
    """Create confirmation token.

    Args:
        email: email to be encoded

    Returns: encoded JWT token
    """
    return _create_jwt_token(
        {"type": "confirmation", "sub": email}, timedelta(hours=24)
    )


def get_subject(token: str, typ: Literal["access", "confirmation"]) -> str:
    """Get subject email from JWT token.

    Args:
        token: encoded JWT token
        typ: token type, either access or confirmation

    Returns: decoded email
    """
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])

    except InvalidTokenError as e:
        raise token_exception from e

    email = payload.get("sub")

    if email is None:
        raise token_exception

    if payload.get("type") != typ:
        raise token_exception

    return email


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
        HTTPException: if user is not found in the database.
    """
    email = get_subject(token, typ="access")
    user = await get_user(conn, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
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

    Raises:
        HTTPException: if user not found in the database or password mismatch.
    """
    user = await authenticate_user(conn, form_data.username, form_data.password)
    return Token(access_token=create_access_token(user["email"]), token_type="bearer")

@router.get("/confirm/{token}")
@log_async_func(logger.info)
async def confirm(token: Token, conn: Annotated[AsyncConnection, Depends(connect_to_db)]) -> dict[str, Any]:
    email = get_subject(token, typ="confirmation")
    user = await get_user(conn, email)
    await users_table.update(conn, user["id"], {"confirmed": True})
    return {"detail": "User confirmed."}
