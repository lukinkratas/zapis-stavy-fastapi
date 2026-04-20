from typing import Any
from httpx import AsyncClient
import pytest

@pytest.mark.integration
@pytest.mark.anyio
async def test_healthcheck(async_client: AsyncClient) -> None:
    response = await async_client.get(f"/")
    assert response.status_code == 200
