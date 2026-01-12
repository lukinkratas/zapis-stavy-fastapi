from typing import Any

import pytest
from httpx import AsyncClient


class TestIntegrationAuth:
    """Integration tests for auth."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_login(
        self, async_client: AsyncClient, default_user: dict[str, Any]
    ) -> None:
        email = default_user["email"]
        password = default_user["password"]
        response = await async_client.post(
            "/token", json={"email": email, "password": password}
        )
        assert response.status_code == 200
