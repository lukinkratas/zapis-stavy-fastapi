from typing import Generator, AsyncGenerator
import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from zapisstavyapi.main import app

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="session")
async def async_client(test_client: TestClient) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=test_client.base_url
    ) as ac:
        yield ac
