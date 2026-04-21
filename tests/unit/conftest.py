import uuid
from datetime import datetime, timezone
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from psycopg import AsyncConnection
from pytest_mock import MockerFixture

from api.db import connect_to_db
from api.main import app
from api.models.users import UsersTable
from api.routers.auth import get_password_hash


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
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
        ) as async_client:
            yield async_client

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user_json(
    mocker: MockerFixture, credentials: dict[str, str]
) -> dict[str, Any]:
    return {
        "email": credentials["email"],
        "password": get_password_hash(credentials["password"]),
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "confirmed": False,
    }


@pytest.fixture
def registered_user(
    mocker: MockerFixture, registered_user_json: dict[str, Any]
) -> dict[str, Any]:
    mocker.patch.object(UsersTable, "select_by_id", return_value=registered_user_json)
    mocker.patch.object(
        UsersTable, "select_by_email", return_value=registered_user_json
    )
    return registered_user_json


@pytest.fixture
def confirmed_user(
    mocker: MockerFixture, registered_user: dict[str, Any]
) -> MockerFixture:
    confirmed_user_json = registered_user.copy()
    confirmed_user_json["confirmed"] = True
    mocker.patch.object(UsersTable, "select_by_id", return_value=confirmed_user_json)
    mocker.patch.object(UsersTable, "select_by_email", return_value=confirmed_user_json)
    return confirmed_user_json
