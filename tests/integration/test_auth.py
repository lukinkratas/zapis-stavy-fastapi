import pytest
from fastapi import HTTPException
from psycopg import AsyncConnection

from api.auth import authenticate_user, get_current_confirmed_user, get_current_user
from api.repositories.users import UserRow


@pytest.mark.integration
@pytest.mark.asyncio
async def test_authenticate_user(
    db_conn: AsyncConnection,
    creds: dict[str, str],
    registered_user: UserRow,
) -> None:
    """Testing expected case."""
    await authenticate_user(db_conn, **creds)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_authenticate_user_not_registered_email(db_conn: AsyncConnection) -> None:
    with pytest.raises(HTTPException):
        await authenticate_user(db_conn, "not@registered.net", "password")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_authenticate_user_invalid_password(
    db_conn: AsyncConnection,
    creds: dict[str, str],
    registered_user: UserRow,
) -> None:
    with pytest.raises(HTTPException):
        await authenticate_user(db_conn, creds["email"], "invalid")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_current_user(
    db_conn: AsyncConnection,
    registered_user: UserRow,
    access_token: str,
) -> None:
    """Testing expected case."""
    await get_current_user(db_conn, access_token)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_current_user_with_expired_access_token(
    db_conn: AsyncConnection,
    registered_user: UserRow,
    expired_access_token: str,
) -> None:
    """Testing access token with different encoded exp."""
    with pytest.raises(HTTPException):
        await get_current_user(db_conn, expired_access_token)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_current_user_with_random_user_access_token(
    db_conn: AsyncConnection,
    registered_user: UserRow,
    random_user_access_token: str,
) -> None:
    """Testing access token with random access token."""
    with pytest.raises(HTTPException):
        await get_current_user(db_conn, random_user_access_token)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_current_user_with_confirmation_token(
    db_conn: AsyncConnection,
    registered_user: UserRow,
    confirmation_token: str,
) -> None:
    """Testing access token with different encoded typ."""
    with pytest.raises(HTTPException):
        await get_current_user(db_conn, confirmation_token)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_current_confirmed_user(
    db_conn: AsyncConnection,
    confirmed_user: UserRow,
) -> None:
    """Testing expected case."""
    assert await get_current_confirmed_user(confirmed_user)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_current_confirmed_user_not_confirmed(
    db_conn: AsyncConnection, registered_user: UserRow
) -> None:
    with pytest.raises(HTTPException):
        await get_current_confirmed_user(registered_user)
