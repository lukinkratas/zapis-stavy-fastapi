from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from psycopg import AsyncConnection
from testcontainers.postgres import PostgresContainer

from api.auth import create_access_token, create_confirmation_token
from api.config import DbSettings
from api.db import get_conn_info
from api.main import app
from api.repositories.users import UserRow

ROOT = Path(__file__).parent.parent.resolve()


@pytest.fixture
def mock_send_email() -> Generator[MagicMock, None, None]:
    msg = (
        {
            "MessageId": "EXAMPLE78603177f-7a5433e7-8edb-42ae-af10-f0181f34d6ee-000000",
            "ResponseMetadata": {},
        },
    )
    with patch("api.routers.auth.ses_send_email", return_value=msg) as mock:
        yield mock


@pytest.fixture(scope="session")
def test_db() -> Generator[PostgresContainer, None, None]:
    with PostgresContainer("postgres:18").with_volume_mapping(
        str(ROOT / "sql" / "init.sql"), "/docker-entrypoint-initdb.d/init.sql"
    ) as postgres:
        yield postgres


@pytest.fixture(scope="session")
def mock_db_settings(test_db: PostgresContainer) -> Generator[MagicMock, None, None]:
    db_settings = DbSettings(
        name=test_db.dbname,
        username=test_db.username,
        password=test_db.password,
        port=str(test_db.get_exposed_port(5432)),
        host=test_db.get_container_host_ip(),
    )
    with patch("api.db.get_db_settings", return_value=db_settings) as mock:
        yield mock


@pytest_asyncio.fixture(scope="session")
async def test_client(mock_db_settings: MagicMock) -> AsyncGenerator[AsyncClient, None]:
    async with app.router.lifespan_context(app):
        app.state.limiter.enabled = False

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            yield client


@pytest_asyncio.fixture
async def db_conn(mock_db_settings: MagicMock) -> AsyncGenerator[AsyncConnection, None]:
    """Create connection."""
    async with await AsyncConnection.connect(conninfo=get_conn_info()) as conn:
        yield conn


@pytest.fixture
def creds() -> dict[str, str]:
    """Used in unit and integration user/register and auth/login tests."""
    return {"email": "test@test.net", "password": "password"}


@pytest.fixture(
    params=[
        pytest.param(
            {"email": "update@test.net", "password": "update"},
            id="email and password update",
        ),
        pytest.param({"email": "update@test.net"}, id="email only"),
        pytest.param({"password": "update"}, id="password only"),
    ]
)
def update_creds(request: pytest.FixtureRequest) -> dict[str, str]:
    """Used in unit and integration user/update tests."""
    return request.param


@pytest.fixture
def props() -> dict[str, str]:
    """Used in unit and integration location/create tests."""
    return {"location_name": "test"}


@pytest.fixture
def update_props() -> dict[str, str]:
    """Used in unit and integration location/update tests."""
    return {"location_name": "update"}


@pytest.fixture
def access_token(registered_user: UserRow) -> str:
    return create_access_token(registered_user.id)


@pytest.fixture
def confirmation_token(registered_user: UserRow) -> str:
    return create_confirmation_token(registered_user.id)
