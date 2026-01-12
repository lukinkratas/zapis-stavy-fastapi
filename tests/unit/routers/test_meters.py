from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.db_models.meters import MetersTable
from api.db_models.readings import ReadingsTable
from tests.assertions import assert_meter


class TestUnitMeter:
    """Unit tests for meters."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_and_delete_meter(
        self,
        async_client: AsyncClient,
        mocker: MockerFixture,
        default_user: dict[str, Any],
        default_meter: dict[str, Any],
    ) -> None:
        # create meter
        mocker.patch.object(
            MetersTable, "insert", new=AsyncMock(return_value=default_meter)
        )
        request_body = {"user_id": default_user["id"], "name": "test"}
        response = await async_client.post("/meter", json=request_body)
        assert response.status_code == 201

        new_meter = response.json()
        assert_meter(new_meter)

        # delete created meter
        mocker.patch.object(MetersTable, "delete", new=AsyncMock(return_value=None))
        mid = new_meter["id"]
        response = await async_client.delete(f"/meter/{mid}")
        assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_meter(
        self,
        mocker: MockerFixture,
        async_client: AsyncClient,
        default_meter: dict[str, Any],
    ) -> None:
        mocker.patch.object(
            MetersTable, "update", new=AsyncMock(return_value=default_meter)
        )
        mid = default_meter["id"]
        request_body = {"name": "update"}
        response = await async_client.put(f"/meter/{mid}", json=request_body)
        assert response.status_code == 200

        updated_meter = response.json()
        assert_meter(updated_meter)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_readings_on_meter(
        self,
        async_client: AsyncClient,
        mocker: MockerFixture,
        default_meter: dict[str, Any],
        default_reading: dict[str, Any],
    ) -> None:
        mocker.patch.object(
            ReadingsTable,
            "select_by_meter_id",
            new=AsyncMock(return_value=[default_reading]),
        )
        mid = default_meter["id"]
        response = await async_client.get(f"/meter/{mid}/reading")
        assert response.status_code == 200
        readings = response.json()
        assert default_reading in readings

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_meter_with_readings(
        self,
        async_client: AsyncClient,
        mocker: MockerFixture,
        default_meter: dict[str, Any],
        default_reading: dict[str, Any],
    ) -> None:
        mocker.patch.object(
            MetersTable, "select_by_id", new=AsyncMock(return_value=default_meter)
        )
        mocker.patch.object(
            ReadingsTable,
            "select_by_meter_id",
            new=AsyncMock(return_value=[default_reading]),
        )
        meter_id = default_meter["id"]
        response = await async_client.get(f"/meter/{meter_id}")
        assert response.status_code == 200
        meter_with_readings = response.json()
        assert meter_with_readings == {
            "meter": default_meter,
            "readings": [default_reading],
        }
