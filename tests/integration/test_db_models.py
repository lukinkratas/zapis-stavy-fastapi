import uuid
from typing import AsyncGenerator

import pytest
from psycopg import AsyncConnection

from zapisstavyapi.db import get_conn_info
from zapisstavyapi.db_models import MetersTable


@pytest.fixture
async def async_conn() -> AsyncGenerator[AsyncConnection, None]:
    async with await AsyncConnection.connect(conninfo=get_conn_info()) as async_conn:
        yield async_conn


@pytest.mark.integration
@pytest.mark.anyio
async def test_retrieve_all_meters(async_conn: AsyncConnection) -> None:
    meters = await MetersTable.retrieve_all(async_conn)
    assert meters


@pytest.mark.integration
@pytest.mark.anyio
async def test_retrieve_meter_by_id(
    async_conn: AsyncConnection, default_meter_id: uuid.UUID
) -> None:
    meters = await MetersTable.retrieve_by_id(async_conn, default_meter_id)
    assert meters
