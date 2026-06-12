import pytest
from httpx import AsyncClient

from api.schemas import BaseResponse


@pytest.mark.integration
@pytest.mark.asyncio
async def test_healthcheck(test_client: AsyncClient) -> None:
    response = await test_client.get("/api/v1/health")
    assert response.status_code == 200
    assert BaseResponse.model_validate(response.json())
