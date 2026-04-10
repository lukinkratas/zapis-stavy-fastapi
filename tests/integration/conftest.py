from datetime import timedelta
from typing import Any, AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from api.auth import create_access_token, create_jwt_token
from api.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    app.state.limiter.enabled = False
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as async_client:
            yield async_client


@pytest.fixture
def random_uuid() -> str:
    return "9f9e8dbc-b2e8-4797-ab97-f0bb08385112"


@pytest.fixture
def credentials() -> dict[str, str]:
    return {"email": "test@test.net", "password": "pswd1234"}


@pytest.fixture
def not_registered_email() -> str:
    return "not.registered@test.net"


@pytest.fixture
def invalid_password() -> str:
    return "invalid"


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
def not_registered_email_token(not_registered_email: str) -> str:
    return create_access_token(not_registered_email)


@pytest.fixture
def expired_access_token(credentials: dict[str, str]) -> str:
    return create_jwt_token(
        {"type": "access", "sub": credentials["email"]}, timedelta(-1)
    )


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
