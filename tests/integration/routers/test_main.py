import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_healthcheck(test_client: AsyncClient) -> None:
    response = await test_client.get("/v1/health")
    assert response.status_code == 200
    assert response.text == "Server is running."
