from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.db_models.meters import MetersTable
from api.db_models.readings import ReadingsTable
from tests.assertions import assert_meter

from ..utils import meter_factory


class TestUnitMeter:
    """Unit tests for meters."""

    @pytest.mark.anyio
    async def test_create_and_delete_meter(
        self,
        async_client: AsyncClient,
        mocker: MockerFixture,
        registered_user: dict[str, Any],
        token: str,
    ) -> None:
        meter_payload = {"name": "new"}

        # mocking
        new_meter = meter_factory(meter_payload, registered_user["id"])
        mocker.patch.object(
            MetersTable, "insert", new=AsyncMock(return_value=new_meter)
        )

        # create meter
        response = await async_client.post(
            "/meter",
            json=meter_payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

        new_meter = response.json()
        assert_meter(new_meter)

        # delete created meter
        mocker.patch.object(MetersTable, "delete", new=AsyncMock(return_value=None))
        mid = new_meter["id"]
        response = await async_client.delete(f"/meter/{mid}")
        assert response.status_code == 200

    @pytest.mark.anyio
    async def test_update_meter(
        self,
        mocker: MockerFixture,
        async_client: AsyncClient,
        created_meter: dict[str, Any],
    ) -> None:
        updated_meter_payload = {"name": "update"}

        # mocking
        updated_meter = created_meter | updated_meter_payload
        mocker.patch.object(
            MetersTable, "update", new=AsyncMock(return_value=updated_meter)
        )

        # update meter
        mid = created_meter["id"]
        response = await async_client.put(f"/meter/{mid}", json=updated_meter_payload)
        assert response.status_code == 200

        updated_meter = response.json()
        assert_meter(updated_meter)

    @pytest.mark.anyio
    async def test_get_readings_on_meter(
        self,
        async_client: AsyncClient,
        mocker: MockerFixture,
        created_meter: dict[str, Any],
        created_reading: dict[str, Any],
    ) -> None:
        mocker.patch.object(
            ReadingsTable,
            "select_by_meter_id",
            new=AsyncMock(return_value=[created_reading]),
        )
        mid = created_meter["id"]
        response = await async_client.get(f"/meter/{mid}/reading")
        assert response.status_code == 200

    @pytest.mark.anyio
    async def test_get_meter_with_readings(
        self,
        async_client: AsyncClient,
        mocker: MockerFixture,
        created_meter: dict[str, Any],
        created_reading: dict[str, Any],
    ) -> None:
        # mocking
        mocker.patch.object(
            MetersTable, "select_by_id", new=AsyncMock(return_value=created_meter)
        )
        mocker.patch.object(
            ReadingsTable,
            "select_by_meter_id",
            new=AsyncMock(return_value=[created_reading]),
        )

        meter_id = created_meter["id"]
        response = await async_client.get(f"/meter/{meter_id}")
        assert response.status_code == 200
        meter_with_readings = response.json()
        assert meter_with_readings == {
            "meter": created_meter,
            "readings": [created_reading],
        }
