import uuid
from typing import Any, AsyncGenerator

import pytest
from httpx import AsyncClient

from tests.assertions import assert_meter, assert_reading
from zapisstavyapi.models import MeterResponseJson, ReadingResponseJson


async def assert_meters(
    async_client: AsyncClient, expected_list_of_meters: list[MeterResponseJson]
) -> None:
    response = await async_client.get("/meter")
    meters = response.json()
    assert meters == expected_list_of_meters


async def assert_readings_on_meter(
    async_client: AsyncClient,
    meter_id: uuid.UUID,
    expected_list_of_readings: list[ReadingResponseJson],
) -> None:
    response = await async_client.get(f"/meter/{meter_id}/reading")
    readings = response.json()
    assert readings == expected_list_of_readings


@pytest.fixture
def default_meter() -> dict[str, Any]:
    return {
        "id": "5ad4f210-cdfb-4196-82f7-af6afda013ea",
        "created_at": "2026-01-03T20:57:12.525797Z",
        "name": "default",
        "description": None,
    }


@pytest.fixture
def default_reading(default_meter: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": "d09b982f-ffe7-42d1-809f-5c61eeac9f99",
        "created_at": "2026-01-03T20:57:12.543268Z",
        "meter_id": default_meter["id"],
        "value": 11.0,
    }


@pytest.fixture
async def created_meter(
    async_client: AsyncClient,
) -> AsyncGenerator[dict[str, Any], None]:
    name = "test"
    response = await async_client.post("/meter", json={"name": name})
    created_meter = response.json()

    yield created_meter

    mid = created_meter["id"]
    await async_client.delete(f"/meter/{mid}")


@pytest.fixture
async def created_reading(
    async_client: AsyncClient, created_meter: dict[str, Any]
) -> AsyncGenerator[dict[str, Any], None]:
    meter_id = created_meter["id"]
    value = 99.0
    response = await async_client.post(
        "/reading", json={"meter_id": meter_id, "value": value}
    )
    created_reading = response.json()

    yield created_reading

    rid = created_reading["id"]
    await async_client.delete(f"/reading/{rid}")


class TestIntegrationMeter:
    """Integration tests for meters."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_all_meters(
        self, async_client: AsyncClient, default_meter: MeterResponseJson
    ) -> None:
        response = await async_client.get("/meter")

        assert response.status_code == 200
        meters = response.json()
        assert meters == [default_meter]

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_and_delete_meter(
        self, async_client: AsyncClient, default_meter: MeterResponseJson
    ) -> None:
        await assert_meters(async_client, [default_meter])

        # create meter
        name = "test"
        response = await async_client.post("/meter", json={"name": name})
        assert response.status_code == 201

        new_meter = response.json()
        assert_meter(new_meter, name=name)

        await assert_meters(async_client, [default_meter, new_meter])

        # delete created meter
        mid = new_meter["id"]
        response = await async_client.delete(f"/meter/{mid}")
        assert response.status_code == 200

        await assert_meters(async_client, [default_meter])

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_meter(
        self, async_client: AsyncClient, created_meter: MeterResponseJson
    ) -> None:
        name = "test_updated"
        mid = created_meter["id"]
        response = await async_client.put(f"/meter/{mid}", json={"name": name})
        assert response.status_code == 200

        updated_meter = response.json()
        assert_meter(updated_meter, name=name)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_readings_on_meter(
        self,
        async_client: AsyncClient,
        default_meter: MeterResponseJson,
        default_reading: ReadingResponseJson,
    ) -> None:
        meter_id = default_meter["id"]
        response = await async_client.get(f"/meter/{meter_id}/reading")
        assert response.status_code == 200
        readings = response.json()
        assert readings == [default_reading]

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_meter_with_readings(
        self,
        async_client: AsyncClient,
        default_meter: MeterResponseJson,
        default_reading: ReadingResponseJson,
    ) -> None:
        meter_id = default_meter["id"]
        response = await async_client.get(f"/meter/{meter_id}")
        assert response.status_code == 200
        meter_with_readings = response.json()
        assert meter_with_readings == {
            "meter": default_meter,
            "readings": [default_reading],
        }


class TestIntegrationReading:
    """Integration tests for readings."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_and_delete_reading(
        self,
        async_client: AsyncClient,
        default_meter: MeterResponseJson,
        default_reading: ReadingResponseJson,
    ) -> None:
        meter_id = default_meter["id"]
        await assert_readings_on_meter(async_client, meter_id, [default_reading])

        # create reading
        value = 99.0
        response = await async_client.post(
            "/reading", json={"meter_id": meter_id, "value": value}
        )
        assert response.status_code == 201

        new_reading = response.json()
        assert_reading(new_reading, value=value)

        await assert_readings_on_meter(
            async_client, meter_id, [default_reading, new_reading]
        )

        # delete created reading
        rid = new_reading["id"]
        response = await async_client.delete(f"/reading/{rid}")
        assert response.status_code == 200

        await assert_readings_on_meter(async_client, meter_id, [default_reading])

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_reading(
        self, async_client: AsyncClient, created_reading: ReadingResponseJson
    ) -> None:
        value = 55.0
        rid = created_reading["id"]
        response = await async_client.put(f"/reading/{rid}", json={"value": value})
        assert response.status_code == 200

        updated_reading = response.json()
        assert_reading(updated_reading, value=value)
