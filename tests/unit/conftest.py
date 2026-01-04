from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from psycopg import AsyncCursor, Connection

from zapisstavyapi.db import db_connect
from zapisstavyapi.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    # Create a mock cursor
    mock_cursor = AsyncMock(spec=AsyncCursor)
    mock_cursor.execute = AsyncMock()
    mock_cursor.__aenter__.return_value = mock_cursor
    mock_cursor.__aexit__.return_value = None

    # Create a mock connection
    mock_conn = AsyncMock(spec=Connection)
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.commit = AsyncMock()
    mock_conn.rollback = AsyncMock()

    # Mock the db_connect dependency to return your mock connection
    async def override_db_connect() -> AsyncGenerator[AsyncMock, None]:
        yield mock_conn

    # Override the dependency in your app
    app.dependency_overrides[db_connect] = override_db_connect

    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as async_client:
            async_client.mock_conn = mock_conn
            async_client.mock_cursor = mock_cursor
            yield async_client

    # Clean up
    app.dependency_overrides.clear()
