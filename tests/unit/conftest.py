import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from psycopg import AsyncConnection

from api.db import connect_to_db
from api.main import app
from api.routers.auth import (
    create_access_token,
    create_confirmation_token,
    get_password_hash,
)


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
def user_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def user_from_db(credentials: dict[str, str], user_id: str) -> dict[str, Any]:
    return {
        "email": credentials["email"],
        "password": get_password_hash(credentials["password"]),
        "id": user_id,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "confirmed": True,
    }


@pytest.fixture
async def access_token(user_id: str) -> str:
    return create_access_token(user_id)


@pytest.fixture
async def confirmation_token(user_id: str) -> str:
    return create_confirmation_token(user_id)


@pytest.fixture
async def expired_confirmation_token(user_id: str) -> str:
    return create_confirmation_token(user_id, expires_delta=timedelta(-1))
