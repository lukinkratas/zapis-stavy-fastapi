from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from psycopg import AsyncConnection

from api.db import connect_to_db
from api.main import app
from api.routers.auth import create_access_token

from .utils import meter_factory, reading_factory, user_factory


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

    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as async_client:
            yield async_client

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def credentials() -> dict[str, str]:
    return {"email": "test@test.net", "password": "pswd1234"}


@pytest.fixture
def registered_user(credentials: dict[str, str]) -> dict[str, Any]:
    return user_factory(credentials)


@pytest.fixture
async def token(credentials: dict[str, str]) -> str:
    return create_access_token(credentials["email"])


@pytest.fixture
async def created_meter(registered_user: dict[str, Any]) -> dict[str, Any]:
    return meter_factory({"name": "test"}, registered_user["id"])


@pytest.fixture
async def created_reading(
    created_meter: dict[str, Any], registered_user: dict[str, Any]
) -> dict[str, Any]:
    return reading_factory(
        {"value": 11.0, "meter_id": created_meter["id"]}, registered_user["id"]
    )
