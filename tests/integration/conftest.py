from typing import Any, AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    # def override_get_settings() -> Settings:
    #     return Settings(
    #         POSTGRES_DB="zapisstavy_dev", POSTGRES_HOST="localhost", ENV="test"
    #     )

    # app.dependency_overrides[get_settings] = override_get_settings

    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as async_client:
            yield async_client


@pytest.fixture
async def registered_user(
    async_client: AsyncClient,
) -> AsyncGenerator[dict[str, Any], None]:
    email = "test@test.net"
    password = "pswd1234"
    response = await async_client.post(
        "/register", json={"email": email, "password": password}
    )
    registered_user = response.json()

    yield registered_user

    uid = registered_user["id"]
    await async_client.delete(f"/user/{uid}")


@pytest.fixture
async def created_meter(
    async_client: AsyncClient, registered_user: dict[str, Any]
) -> AsyncGenerator[dict[str, Any], None]:
    user_id = registered_user["id"]
    name = "test"
    response = await async_client.post(
        "/meter", json={"user_id": user_id, "name": name}
    )
    created_meter = response.json()

    yield created_meter

    mid = created_meter["id"]
    await async_client.delete(f"/meter/{mid}")


@pytest.fixture
async def created_reading(
    async_client: AsyncClient, created_meter: dict[str, Any]
) -> AsyncGenerator[dict[str, Any], None]:
    meter_id = created_meter["id"]
    value = 99.0
    response = await async_client.post(
        "/reading", json={"meter_id": meter_id, "value": value}
    )
    created_reading = response.json()

    yield created_reading

    rid = created_reading["id"]
    await async_client.delete(f"/reading/{rid}")
