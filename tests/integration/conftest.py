import os
import uuid
from datetime import timedelta
from pathlib import Path
from typing import Any, AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from testcontainers.postgres import PostgresContainer

from api.main import app
from api.routers.auth import (
    create_access_token,
    create_confirmation_token,
)

ROOT = Path(__file__).parent.parent.parent.resolve()


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    app.state.limiter.enabled = False

    with (
        PostgresContainer("postgres:14")
        .with_volume_mapping(
            str(ROOT / "scripts/init-db.sh"), "/docker-entrypoint-initdb.d/init-db.sh"
        )
        .with_volume_mapping(
            str(ROOT / "sql/"), "/docker-entrypoint-initdb.d/sql/"
        ) as postgres
    ):
        os.environ["DB_NAME"] = postgres.dbname
        os.environ["DB_USERNAME"] = postgres.username
        os.environ["DB_PASSWORD"] = postgres.password
        os.environ["DB_PORT"] = str(postgres.get_exposed_port(5432))
        os.environ["DB_HOST"] = postgres.get_container_host_ip()

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
    registered_user = response.json()["user"]

    yield registered_user

    uid = registered_user["id"]
    await async_client.delete(f"/user/{uid}")


@pytest.fixture
def access_token(async_client: AsyncClient, registered_user: dict[str, str]) -> str:
    return create_access_token(registered_user["id"])


@pytest.fixture
def not_registered_email_token(not_registered_email: str) -> str:
    return create_access_token(uuid.uuid4())


@pytest.fixture
def expired_access_token(registered_user: dict[str, str]) -> str:
    return create_access_token(uuid.uuid4(), timedelta(-1))


@pytest.fixture
def confirmation_token(registered_user: dict[str, str]) -> str:
    return create_confirmation_token(registered_user["id"])


@pytest.fixture
async def created_location(
    async_client: AsyncClient, access_token: str
) -> AsyncGenerator[dict[str, Any], None]:
    request_body = {"name": "test"}
    response = await async_client.post(
        "/location",
        json=request_body,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    created_location = response.json()

    yield created_location

    mid = created_location["id"]
    await async_client.delete(f"/location/{mid}")
