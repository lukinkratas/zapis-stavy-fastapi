from typing import Any

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.schemas import Token


class TestLogin:
    """Integration tests for login endpoint."""

    @pytest.mark.asyncio
    async def test_login_registered_user(
        self,
        test_client: AsyncClient,
        mocker: MockerFixture,
        creds: dict[str, str],
        registered_user: dict[str, Any],
    ) -> None:
        data = {
            "username": creds["email"],
            "password": creds["password"],  # plain password
        }
        response = await test_client.post("/v1/auth/token", data=data)
        assert response.status_code == 200

        token = response.json()
        assert Token.model_validate(token)


class TestConfirm:
    """Integration tests for confirm endpoint."""

    @pytest.mark.asyncio
    async def test_confirm_registered_user(
        self,
        test_client: AsyncClient,
        mocker: MockerFixture,
        registered_user: dict[str, Any],
        confirmation_token: str,
    ) -> None:
        response = await test_client.get(f"/v1/auth/confirm/{confirmation_token}")
        assert response.status_code == 200
