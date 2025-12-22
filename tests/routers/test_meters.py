import pytest
from httpx import AsyncClient

from zapisstavyapi.models.utility import Meter, MeterWithReadings, Reading
from zapisstavyapi.routers.utility import MeterDict, ReadingDict


async def create_meter(name: str, async_client: AsyncClient) -> MeterDict:
    response = await async_client.post('/meter', json={'name': name})
    return response.json()


async def create_reading(
    value: float, meter_id: str, async_client: AsyncClient
) -> ReadingDict:
    response = await async_client.post(
        '/reading', json={'value': value, 'meter_id': meter_id}
    )
    return response.json()


@pytest.fixture
async def created_meter(async_client: AsyncClient) -> MeterDict:
    return await create_meter('test', async_client)


@pytest.fixture
async def created_reading(
    async_client: AsyncClient, created_meter: MeterDict
) -> ReadingDict:
    return await create_reading(99.0, created_meter['meter_id'], async_client)


@pytest.mark.anyio
async def test_create_meter(async_client: AsyncClient) -> None:
    name = 'test'
    response = await async_client.post('/meter', json={'name': name})

    assert response.status_code == 201

    response_json = response.json()
    assert Meter.model_validate(response_json)
    assert response_json['name'] == name


@pytest.mark.anyio
async def test_create_meter_missing_data(async_client: AsyncClient) -> None:
    reponse = await async_client.post('/meter', json={})

    assert reponse.status_code == 422


@pytest.mark.anyio
async def test_get_all_meters(
    async_client: AsyncClient, created_meter: MeterDict
) -> None:
    response = await async_client.get('/meter')

    assert response.status_code == 200
    assert response.json() == [created_meter]


@pytest.mark.anyio
async def test_create_reading(
    async_client: AsyncClient, created_meter: MeterDict
) -> None:
    value = 99.0
    response = await async_client.post(
        '/reading', json={'value': value, 'meter_id': created_meter['meter_id']}
    )

    assert response.status_code == 201

    response_json = response.json()
    assert Reading.model_validate(response_json)
    assert response_json['value'] == value
    assert response_json['meter_id'] == created_meter['meter_id']


@pytest.mark.anyio
async def test_get_readings_on_meter(
    async_client: AsyncClient, created_meter: MeterDict, created_reading: ReadingDict
) -> None:
    meter_id = created_meter['meter_id']
    response = await async_client.get(f'/meter/{meter_id}/reading')

    assert response.status_code == 200
    assert response.json() == [created_reading]


@pytest.mark.anyio
async def test_get_readings_on_meter_empty(
    async_client: AsyncClient, created_meter: MeterDict
) -> None:
    meter_id = created_meter['meter_id']
    response = await async_client.get(f'/meter/{meter_id}/reading')

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_get_meter_with_readings(
    async_client: AsyncClient, created_meter: MeterDict, created_reading: ReadingDict
) -> None:
    meter_id = created_meter['meter_id']
    response = await async_client.get(f'/meter/{meter_id}')

    assert response.status_code == 200

    response_json = response.json()
    assert MeterWithReadings.model_validate(response_json)
    assert response_json['meter'] == created_meter
    assert response_json['readings'] == [created_reading]


@pytest.mark.anyio
async def test_get_missing_meter_with_readings(
    async_client: AsyncClient, created_meter: MeterDict, created_reading: ReadingDict
) -> None:
    response = await async_client.get('/meter/xxx')

    assert response.status_code == 404
