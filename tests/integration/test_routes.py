import uuid
from typing import Any

import pytest
from httpx import AsyncClient

from zapisstavyapi.models import (
    MeterResp,
)


@pytest.fixture
def default_meter(default_meter_id: uuid.UUID) -> dict[str, Any]:
    return {
        "name": "default",
        "id": default_meter_id,
        "created_at": "2026-01-01T13:00:52.176660Z",
    }


@pytest.mark.integration
@pytest.mark.anyio
async def test_get_all_meters(
    async_client: AsyncClient, default_meter: MeterResp
) -> None:
    response = await async_client.get("/meter")

    assert response.status_code == 200
    assert response.json() == [default_meter]


# @pytest.fixture
# async def created_meter(async_client: AsyncClient) -> dict[str, str]:
#     name = "test"
#     response = await async_client.post("/meter", json={"name": name})
#     return response.json()
#
#
# @pytest.fixture
# async def created_reading(
#     async_client: AsyncClient, created_meter: dict[str, Any]
# ) -> dict[str, Any]:
#     value = 99.0
#     meter_id = created_meter["meter_id"]
#     response = await async_client.post(
#         "/reading", json={"value": value, "meter_id": meter_id}
#     )
#     return response.json()
#
#
# @pytest.mark.anyio
# async def test_create_meter(async_client: AsyncClient) -> None:
#     name = "test"
#     response = await async_client.post("/meter", json={"name": name})
#
#     assert response.status_code == 201
#
#     response_json = response.json()
#     assert MeterResp.model_validate(response_json)
#     assert response_json["name"] == name
#
#
# @pytest.mark.anyio
# async def test_create_meter_missing_data(async_client: AsyncClient) -> None:
#     reponse = await async_client.post("/meter", json={})
#
#     assert reponse.status_code == 422
#
#
#
#
# @pytest.mark.anyio
# async def test_create_reading(
#     async_client: AsyncClient, created_meter: dict[str, Any]
# ) -> None:
#     value = 99.0
#     response = await async_client.post(
#         "/reading", json={"value": value, "meter_id": created_meter["mid"]}
#     )
#
#     assert response.status_code == 201
#
#     response_json = response.json()
#     assert ReadingResp.model_validate(response_json)
#     assert response_json["value"] == value
#     assert response_json["meter_id"] == created_meter["mid"]
#
#
# @pytest.mark.anyio
# async def test_get_readings_on_meter(
#     async_client: AsyncClient,
#     created_meter: dict[str, Any],
#     created_reading: dict[str, Any],
# ) -> None:
#     meter_id = created_meter["mid"]
#     response = await async_client.get(f"/meter/{meter_id}/reading")
#
#     assert response.status_code == 200
#     assert response.json() == [created_reading]
#
#
# @pytest.mark.anyio
# async def test_get_readings_on_meter_empty(
#     async_client: AsyncClient, created_meter: dict[str, Any]
# ) -> None:
#     meter_id = created_meter["mid"]
#     response = await async_client.get(f"/meter/{meter_id}/reading")
#
#     assert response.status_code == 200
#     assert response.json() == []
#
#
# @pytest.mark.anyio
# async def test_get_meter_with_readings(
#     async_client: AsyncClient,
#     created_meter: dict[str, Any],
#     created_reading: dict[str, Any],
# ) -> None:
#     meter_id = created_meter["mid"]
#     response = await async_client.get(f"/meter/{meter_id}")
#
#     assert response.status_code == 200
#
#     response_json = response.json()
#     assert MeterWithReadingsResp.model_validate(response_json)
#     assert response_json["meter"] == created_meter
#     assert response_json["readings"] == [created_reading]
#
#
# @pytest.mark.anyio
# async def test_get_missing_meter_with_readings(
#     async_client: AsyncClient,
#     created_meter: dict[str, Any],
#     created_reading: dict[str, Any],
# ) -> None:
#     response = await async_client.get("/meter/xxx")
#
#     assert response.status_code == 404
