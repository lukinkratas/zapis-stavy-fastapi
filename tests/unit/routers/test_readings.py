from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.db_models.readings import ReadingsTable
from tests.assertions import assert_reading


class TestUnitReading:
    """Unit tests for readings."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_and_delete_reading(
        self,
        mocker: MockerFixture,
        async_client: AsyncClient,
        default_meter: dict[str, Any],
        default_reading: dict[str, Any],
    ) -> None:
        # create reading
        mocker.patch.object(
            ReadingsTable, "insert", new=AsyncMock(return_value=default_reading)
        )
        request_body = {"meter_id": default_meter["id"], "value": 99.0}
        response = await async_client.post("/reading", json=request_body)
        assert response.status_code == 201

        new_reading = response.json()
        assert_reading(new_reading)

        # delete created reading
        mocker.patch.object(ReadingsTable, "delete", new=AsyncMock(return_value=None))
        rid = new_reading["id"]
        response = await async_client.delete(f"/reading/{rid}")
        assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_reading(
        self,
        async_client: AsyncClient,
        mocker: MockerFixture,
        default_reading: dict[str, Any],
    ) -> None:
        mocker.patch.object(
            ReadingsTable, "update", new=AsyncMock(return_value=default_reading)
        )
        rid = default_reading["id"]
        request_body = {"value": 55.0}
        response = await async_client.put(f"/reading/{rid}", json=request_body)
        assert response.status_code == 200

        updated_reading = response.json()
        assert_reading(updated_reading)
