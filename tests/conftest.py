from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from zapisstavyapi.main import app
from zapisstavyapi.routers.utility import meters_table, readings_table


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    yield TestClient(app)


@pytest.fixture
async def async_client(client: TestClient) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=client.base_url
    ) as ac:
        yield ac


@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator[None, None]:
    meters_table.clear()
    readings_table.clear()
    yield
