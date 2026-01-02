from typing import Any, AsyncGenerator

import pytest
from httpx import AsyncClient

from zapisstavyapi.models import MeterResponseJson


@pytest.fixture
def default_meter() -> dict[str, Any]:
    return {
        "name": "default",
        "id": "5ad4f210-cdfb-4196-82f7-af6afda013ea",
        "created_at": "2026-01-02T11:07:19.693516Z",
        "description": None,
    }


@pytest.fixture
async def created_meter(
    async_client: AsyncClient,
) -> AsyncGenerator[dict[str, Any], None]:
    name = "test"
    response = await async_client.post("/meter", json={"name": name})
    created_meter = response.json()

    yield created_meter

    id = created_meter["id"]
    await async_client.delete(f"/meter/{id}")


@pytest.mark.integration
@pytest.mark.anyio
async def test_get_all_meters(
    async_client: AsyncClient, default_meter: MeterResponseJson
) -> None:
    response = await async_client.get("/meter")

    assert response.status_code == 200
    meters = response.json()
    assert meters == [default_meter]


@pytest.mark.integration
@pytest.mark.anyio
async def test_create_and_delete_meter(
    async_client: AsyncClient, default_meter: MeterResponseJson
) -> None:
    # assert meters
    response = await async_client.get("/meter")
    meters = response.json()
    assert meters == [default_meter]

    # create meter
    name = "test"
    response = await async_client.post("/meter", json={"name": name})
    assert response.status_code == 201

    # assert meter
    new_meter = response.json()
    assert MeterResponseJson.model_validate(new_meter)
    assert new_meter["name"] == name

    # assert meters
    response = await async_client.get("/meter")
    meters = response.json()
    assert meters == [default_meter, new_meter]

    # delete created meter
    id = new_meter["id"]
    response = await async_client.delete(f"/meter/{id}")
    assert response.status_code == 200

    # assert meters
    response = await async_client.get("/meter")
    meters = response.json()
    assert meters == [default_meter]


@pytest.mark.integration
@pytest.mark.anyio
async def test_update_meter(
    async_client: AsyncClient, created_meter: MeterResponseJson
) -> None:
    name = "test_updated"
    id = created_meter["id"]
    response = await async_client.put(f"/meter/{id}", json={"name": name})
    assert response.status_code == 200

    # assert meter
    updated_meter = response.json()
    assert MeterResponseJson.model_validate(updated_meter)
    assert updated_meter["name"] == name


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
#     assert MeterResponseJson.model_validate(response_json)
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
