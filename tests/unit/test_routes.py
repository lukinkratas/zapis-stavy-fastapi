from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from api.models.meters import MeterResponseJson
from api.models.users import UserResponseJson
from tests.assertions import assert_meter, assert_reading


class TestUnitMeter:
    """Unit tests for meters."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_all_meters(
        self, async_client: AsyncClient, default_meter: MeterResponseJson
    ) -> None:
        async_client.mock_cursor.fetchall = AsyncMock(return_value=[default_meter])
        response = await async_client.get("/meter")

        assert response.status_code == 200
        meters = response.json()
        assert meters == [default_meter]

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_and_delete_meter(
        self, async_client: AsyncClient, default_user: UserResponseJson, default_meter: MeterResponseJson
    ) -> None:
        async_client.mock_cursor.fetchone = AsyncMock(return_value=default_meter)
        # create meter
        user_id = default_user["id"]
        name = "default"
        response = await async_client.post("/meter", json={"user_id": user_id, "name": name})
        assert response.status_code == 201

        new_meter = response.json()
        assert_meter(new_meter, name=name)

        # delete created meter
        mid = new_meter["id"]
        response = await async_client.delete(f"/meter/{mid}")
        assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_meter(
        self, async_client: AsyncClient, default_meter: dict[str, Any]
    ) -> None:
        async_client.mock_cursor.fetchone = AsyncMock(return_value=default_meter)
        name = "default"
        mid = default_meter["id"]
        response = await async_client.put(f"/meter/{mid}", json={"name": name})
        assert response.status_code == 200

        updated_meter = response.json()
        assert_meter(updated_meter, name=name)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_readings_on_meter(
        self,
        async_client: AsyncClient,
        default_meter: dict[str, Any],
        default_reading: dict[str, Any],
    ) -> None:
        async_client.mock_cursor.fetchall = AsyncMock(return_value=[default_reading])
        meter_id = default_meter["id"]
        response = await async_client.get(f"/meter/{meter_id}/reading")
        assert response.status_code == 200
        readings = response.json()
        assert readings == [default_reading]


#  @pytest.mark.integration
#  @pytest.mark.anyio
#  async def test_get_meter_with_readings(
#      self,
#      async_client: AsyncClient,
#      default_meter: MeterResponseJson,
#      default_reading: ReadingResponseJson,
#  ) -> None:
#      meter_id = default_meter["id"]
#      response = await async_client.get(f"/meter/{meter_id}")
#      assert response.status_code == 200
#      meter_with_readings = response.json()
#      assert meter_with_readings == {
#          "meter": default_meter,
#          "readings": [default_reading],
#      }


class TestIntegrationReading:
    """Unit tests for readings."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_and_delete_reading(
        self,
        async_client: AsyncClient,
        default_meter: dict[str, Any],
        default_reading: dict[str, Any],
    ) -> None:
        async_client.mock_cursor.fetchone = AsyncMock(return_value=default_reading)
        meter_id = default_meter["id"]

        # create reading
        value = 11.0
        response = await async_client.post(
            "/reading", json={"meter_id": meter_id, "value": value}
        )
        assert response.status_code == 201

        new_reading = response.json()
        assert_reading(new_reading, value=value)

        # delete created reading
        rid = new_reading["id"]
        response = await async_client.delete(f"/reading/{rid}")
        assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_reading(
        self, async_client: AsyncClient, default_reading: dict[str, Any]
    ) -> None:
        async_client.mock_cursor.fetchone = AsyncMock(return_value=default_reading)
        value = 11.0
        rid = default_reading["id"]
        response = await async_client.put(f"/reading/{rid}", json={"value": value})
        assert response.status_code == 200

        updated_reading = response.json()
        assert_reading(updated_reading, value=value)
