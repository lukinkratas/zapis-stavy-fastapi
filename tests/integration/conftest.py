import uuid
from datetime import timedelta
from typing import AsyncGenerator
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from psycopg import AsyncConnection

from api.auth import create_access_token, create_confirmation_token
from api.models.locations import LocationRow
from api.models.users import UserRow
from api.services.auth import confirm_user
from api.services.locations import create_location, delete_location
from api.services.users import delete_user, register_user


@pytest_asyncio.fixture
async def registered_user(
    db_conn: AsyncConnection, creds: dict[str, str], mock_send_email: MagicMock
) -> AsyncGenerator[UserRow, None]:
    user = await register_user(db_conn, **creds)
    yield user
    await delete_user(db_conn, user.id)


@pytest_asyncio.fixture
async def confirmed_user(db_conn: AsyncConnection, registered_user: UserRow) -> UserRow:
    return await confirm_user(db_conn, registered_user.id)


@pytest_asyncio.fixture
async def other_user(
    db_conn: AsyncConnection, mock_send_email: MagicMock
) -> AsyncGenerator[UserRow, None]:
    other_creds = {"email": "other@test.net", "password": "password"}
    user = await register_user(db_conn, **other_creds)
    user = await confirm_user(db_conn, user.id)
    yield user
    await delete_user(db_conn, user.id)


@pytest_asyncio.fixture
async def created_location(
    db_conn: AsyncConnection,
    confirmed_user: UserRow,
    location_payload: dict[str, str],
) -> AsyncGenerator[LocationRow, None]:
    location = await create_location(db_conn, confirmed_user.id, **location_payload)
    yield location
    await delete_location(db_conn, location.id, confirmed_user.id)


@pytest.fixture
def expired_access_token(registered_user: UserRow) -> str:
    return create_access_token(registered_user, expires_delta=timedelta(-1))


@pytest.fixture
def expired_confirmation_token(registered_user: UserRow) -> str:
    return create_confirmation_token(registered_user, expires_delta=timedelta(-1))


@pytest.fixture
def other_user_access_token(other_user: UserRow) -> str:
    return create_access_token(other_user.id)


# @pytest.fixture
# def other_user_confirmation_token(other_user: UserRow) -> str:
#     return create_confirmation_token(other_user.id)


@pytest.fixture
def random_user_access_token() -> str:
    return create_access_token(uuid.uuid4())


@pytest.fixture
def random_user_confirmation_token() -> str:
    return create_confirmation_token(uuid.uuid4())
