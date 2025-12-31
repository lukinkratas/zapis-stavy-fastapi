from typing import Any

import pytest
from httpx import AsyncClient

from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from zapisstavyapi.main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    yield TestClient(app)


@pytest.fixture
async def async_client(client: TestClient) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=client.base_url
    ) as ac:
        yield ac


# @pytest.fixture(autouse=True)
# async def db() -> AsyncGenerator[None, None]:
#     await database.connect()
#     yield
#     await database.disconnect()

@pytest.fixture
async def created_meter() -> dict[str, str]:
    return {
        "name": "test",
        "id": "d94a9acf-3775-4dfd-a98f-a4dfea7a241f"
    }

@pytest.fixture
async def created_reading(created_meter: dict[str, Any]) -> dict[str, Any]:
    return {
        "value": 99.0,
        "meter_id": created_meter["id"]
        "id": "1d217e48-cd24-44ba-ae8d-5c57dac723b1",
    }


@pytest.mark.anyio
async def test_create_meter(async_client: AsyncClient) -> None:
    name = "test"
    response = await async_client.post("/meter", json={"name": name})

    assert response.status_code == 201

    response_json = response.json()
    assert Meter.model_validate(response_json)
    assert response_json["name"] == name


@pytest.mark.anyio
async def test_create_meter_missing_data(async_client: AsyncClient) -> None:
    reponse = await async_client.post("/meter", json={})

    assert reponse.status_code == 422


@pytest.mark.anyio
async def test_get_all_meters(
    async_client: AsyncClient, created_meter: dict[str, Any]
) -> None:
    response = await async_client.get("/meter")

    assert response.status_code == 200
    assert response.json() == [created_meter]


@pytest.mark.anyio
async def test_create_reading(
    async_client: AsyncClient, created_meter: dict[str, Any]
) -> None:
    value = 99.0
    response = await async_client.post(
        "/reading", json={"value": value, "meter_id": created_meter["mid"]}
    )

    assert response.status_code == 201

    response_json = response.json()
    assert Reading.model_validate(response_json)
    assert response_json["value"] == value
    assert response_json["meter_id"] == created_meter["mid"]


@pytest.mark.anyio
async def test_get_readings_on_meter(
    async_client: AsyncClient,
    created_meter: dict[str, Any],
    created_reading: dict[str, Any],
) -> None:
    meter_id = created_meter["mid"]
    response = await async_client.get(f"/meter/{meter_id}/reading")

    assert response.status_code == 200
    assert response.json() == [created_reading]


@pytest.mark.anyio
async def test_get_readings_on_meter_empty(
    async_client: AsyncClient, created_meter: dict[str, Any]
) -> None:
    meter_id = created_meter["mid"]
    response = await async_client.get(f"/meter/{meter_id}/reading")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_get_meter_with_readings(
    async_client: AsyncClient,
    created_meter: dict[str, Any],
    created_reading: dict[str, Any],
) -> None:
    meter_id = created_meter["mid"]
    response = await async_client.get(f"/meter/{meter_id}")

    assert response.status_code == 200

    response_json = response.json()
    assert MeterWithReadings.model_validate(response_json)
    assert response_json["meter"] == created_meter
    assert response_json["readings"] == [created_reading]


@pytest.mark.anyio
async def test_get_missing_meter_with_readings(
    async_client: AsyncClient,
    created_meter: dict[str, Any],
    created_reading: dict[str, Any],
) -> None:
    response = await async_client.get("/meter/xxx")

    assert response.status_code == 404
