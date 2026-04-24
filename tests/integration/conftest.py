import os
import uuid
from datetime import timedelta
from pathlib import Path
from typing import Any, AsyncGenerator
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from psycopg import AsyncConnection
from testcontainers.postgres import PostgresContainer

from api.db import get_conn_info
from api.main import app
from api.models.users import users_table
from api.routers.auth import create_access_token, create_confirmation_token

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
async def db_conn() -> AsyncGenerator[AsyncConnection, None]:
    async with await AsyncConnection.connect(conninfo=get_conn_info()) as conn:
        yield conn


@pytest.fixture
async def registered_user(
    async_client: AsyncClient,
    credentials: dict[str, str],
    mock_send_email: MagicMock,
) -> AsyncGenerator[dict[str, Any], None]:
    mock_send_email.reset_mock()
    response = await async_client.post("/register", json=credentials)

    registered_user = response.json()["user"]
    yield registered_user

    access_token = create_access_token(registered_user["id"])
    response = await async_client.delete(
        "/user", headers={"Authorization": f"Bearer {access_token}"}
    )


@pytest.fixture
async def confirmed_user(
    async_client: AsyncClient,
    registered_user: dict[str, Any],
    db_conn: AsyncConnection,
) -> dict[str, Any]:
    return await users_table.update(db_conn, registered_user["id"], {"confirmed": True})


@pytest.fixture
async def created_location(
    async_client: AsyncClient,
    location_payload: dict[str, str],
    access_token: str,
    confirmed_user: dict[str, Any],
) -> AsyncGenerator[dict[str, Any], None]:
    response = await async_client.post(
        "/location",
        json=location_payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    created_location = response.json()

    yield created_location

    location_id = created_location["id"]
    await async_client.delete(f"/location/{location_id}")


@pytest.fixture
def location_id(created_location: dict[str, str]) -> str:
    return created_location["id"]


@pytest.fixture
async def other_confirmed_user(
    async_client: AsyncClient,
    db_conn: AsyncConnection,
    mock_send_email: MagicMock,
) -> AsyncGenerator[dict[str, Any], None]:
    mock_send_email.reset_mock()
    other_creds = {"email": "other@test.net", "password": "password"}
    response = await async_client.post("/register", json=other_creds)

    other_user = response.json()["user"]
    await users_table.update(db_conn, other_user["id"], {"confirmed": True})
    yield other_user

    access_token = create_access_token(other_user["id"])
    response = await async_client.delete(
        "/user", headers={"Authorization": f"Bearer {access_token}"}
    )


@pytest.fixture
async def expired_access_token(registered_user: dict[str, Any]) -> str:
    return create_access_token(registered_user["id"], expires_delta=timedelta(-1))


@pytest.fixture
async def expired_confirmation_token(registered_user: dict[str, Any]) -> str:
    return create_confirmation_token(registered_user["id"], expires_delta=timedelta(-1))


@pytest.fixture
def other_user_access_token(other_confirmed_user: dict[str, Any]) -> str:
    return create_access_token(other_confirmed_user["id"])


@pytest.fixture
async def other_user_confirmation_token(other_confirmed_user: dict[str, Any]) -> str:
    return create_confirmation_token(other_confirmed_user["id"])

@pytest.fixture
def not_registered_user_access_token() -> str:
    return create_access_token(str(uuid.uuid4()))


@pytest.fixture
async def not_registered_user_confirmation_token() -> str:
    return create_confirmation_token(str(uuid.uuid4()))
