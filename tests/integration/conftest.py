from typing import Any, AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as async_client:
            yield async_client


@pytest.fixture
def credentials() -> dict[str, str]:
    return {"email": "test@test.net", "password": "pswd1234"}


@pytest.fixture
async def registered_user(
    async_client: AsyncClient, credentials: dict[str, str]
) -> AsyncGenerator[dict[str, Any], None]:
    response = await async_client.post("/register", json=credentials)
    registered_user = response.json()

    yield registered_user

    uid = registered_user["id"]
    await async_client.delete(f"/user/{uid}")


@pytest.fixture
async def token(
    async_client: AsyncClient,
    credentials: dict[str, str],
    registered_user: dict[str, str],
) -> str:
    # requires user to be registered, credentials are not sufficient
    data = {
        "username": credentials["email"],
        "password": credentials["password"],
    }
    response = await async_client.post(
        "/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = response.json()
    return token["access_token"]


@pytest.fixture
async def created_meter(
    async_client: AsyncClient, token: str
) -> AsyncGenerator[dict[str, Any], None]:
    request_body = {"name": "test"}
    response = await async_client.post(
        "/meter",
        json=request_body,
        headers={"Authorization": f"Bearer {token}"},
    )
    created_meter = response.json()

    yield created_meter

    mid = created_meter["id"]
    await async_client.delete(f"/meter/{mid}")


@pytest.fixture
async def created_reading(
    async_client: AsyncClient, created_meter: dict[str, Any], token: str
) -> AsyncGenerator[dict[str, Any], None]:
    request_body = {"meter_id": created_meter["id"], "value": 99.0}
    response = await async_client.post(
        "/reading",
        json=request_body,
        headers={"Authorization": f"Bearer {token}"},
    )
    created_reading = response.json()

    yield created_reading

    rid = created_reading["id"]
    await async_client.delete(f"/reading/{rid}")
