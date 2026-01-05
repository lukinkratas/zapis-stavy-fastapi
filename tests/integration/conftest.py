from typing import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient

from zapisstavyapi.config import Settings
from zapisstavyapi.main import app, get_settings


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    def override_get_settings() -> Generator[Settings, None]:
        return Settings(
            POSTGRES_DB="zapisstavy_test", POSTGRES_HOST="localhost", ENV_STATE="test"
        )

    app.dependency_overrides[get_settings] = override_get_settings

    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as async_client:
            yield async_client
