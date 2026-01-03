from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from zapisstavyapi.models import MeterResponseJson


@pytest.fixture
def default_meter() -> dict[str, Any]:
    return {
        "id": "5ad4f210-cdfb-4196-82f7-af6afda013ea",
        "created_at": "2026-01-02T20:26:08.445065Z",
        "name": "default",
        "description": None,
    }


@pytest.mark.integration
@pytest.mark.anyio
async def test_get_all_meters(
    async_client: AsyncClient, default_meter: MeterResponseJson
) -> None:
    async_client.mock_cursor.fetchall = AsyncMock(return_value=[default_meter])
    response = await async_client.get("/meter")

    assert response.status_code == 200
    meters = response.json()
    assert meters == [default_meter]


@pytest.mark.integration
@pytest.mark.anyio
async def test_create_and_delete_meter(
    async_client: AsyncClient, default_meter: MeterResponseJson
) -> None:
    async_client.mock_cursor.fetchone = AsyncMock(return_value=default_meter)
    # create meter
    name = "default"
    response = await async_client.post("/meter", json={"name": name})
    assert response.status_code == 201

    # assert meter
    new_meter = response.json()
    assert MeterResponseJson.model_validate(new_meter)
    assert new_meter["name"] == name

    # delete created meter
    mid = new_meter["id"]
    response = await async_client.delete(f"/meter/{mid}")
    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.anyio
async def test_update_meter(
    async_client: AsyncClient, default_meter: MeterResponseJson
) -> None:
    async_client.mock_cursor.fetchone = AsyncMock(return_value=default_meter)
    name = "default"
    mid = default_meter["id"]
    response = await async_client.put(f"/meter/{mid}", json={"name": name})
    assert response.status_code == 200

    # assert meter
    updated_meter = response.json()
    assert MeterResponseJson.model_validate(updated_meter)
    assert updated_meter["name"] == name
