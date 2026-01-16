from typing import Any

import pytest
from httpx import AsyncClient

from tests.assertions import assert_token


class TestIntegrationAuth:
    """Integration tests for auth."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_login(
        self,
        async_client: AsyncClient,
        credentials: dict[str, str],
        registered_user: dict[str, Any],
    ) -> None:
        # requires user to be registered
        data = {
            "username": credentials["email"],
            "password": credentials["password"],
        }
        response = await async_client.post(
            "/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200

        token = response.json()
        assert_token(token)
