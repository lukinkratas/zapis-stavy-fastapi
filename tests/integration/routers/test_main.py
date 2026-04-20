import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.anyio
async def test_healthcheck(async_client: AsyncClient) -> None:
    response = await async_client.get("/")
    assert response.status_code == 200
