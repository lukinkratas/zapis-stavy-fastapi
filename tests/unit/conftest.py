import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from psycopg import AsyncConnection
from pytest_mock import MockerFixture

from api.db import connect_to_db
from api.main import app
from api.repositories.locations import LocationRow
from api.repositories.users import UserRow, UsersTable
from api.security import get_password_hash


@pytest_asyncio.fixture(scope="session")
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    # Create a mock connection
    mock_conn = AsyncMock(spec=AsyncConnection)

    # Mock the dependency to return your mock connection
    async def override_connect_to_db() -> AsyncGenerator[AsyncMock, None]:
        yield mock_conn

    # Override the dependency in your app
    app.dependency_overrides[connect_to_db] = override_connect_to_db

    app.state.limiter.enabled = False

    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            yield client

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user_row(mocker: MockerFixture, creds: dict[str, str]) -> UserRow:
    return UserRow(
        id=uuid.uuid4(),
        created_at=datetime.now(timezone.utc),
        email=creds["email"],
        password_hash=get_password_hash(creds["password"]),
        confirmed=False,
    )


@pytest.fixture
def registered_user(mocker: MockerFixture, registered_user_row: UserRow) -> UserRow:
    mocker.patch.object(UsersTable, "select_by_id", return_value=registered_user_row)
    mocker.patch.object(UsersTable, "select_by_email", return_value=registered_user_row)
    return registered_user_row


@pytest.fixture
def confirmed_user(mocker: MockerFixture, registered_user: UserRow) -> UserRow:
    confirmed_user_row = registered_user._replace(confirmed=True)
    mocker.patch.object(UsersTable, "select_by_id", return_value=confirmed_user_row)
    mocker.patch.object(UsersTable, "select_by_email", return_value=confirmed_user_row)
    return confirmed_user_row


@pytest.fixture
def location_row(props: dict[str, str]) -> LocationRow:
    return LocationRow(
        id=uuid.uuid4(),
        created_at=datetime.now(timezone.utc),
        user_id=uuid.uuid4(),
        **props,
    )
