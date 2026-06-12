import pytest
from httpx import AsyncClient

from api.repositories.users import UserRow
from api.schemas import BaseResponse, TokenResponse


class TestLogin:
    """Integration tests for login endpoint."""

    @pytest.mark.asyncio
    async def test_login_registered_user(
        self,
        test_client: AsyncClient,
        creds: dict[str, str],
        registered_user: UserRow,
    ) -> None:
        data = {
            "username": creds["email"],
            "password": creds["password"],  # plain password
        }
        response = await test_client.post("/api/v1/auth/token", data=data)
        assert response.status_code == 200
        assert TokenResponse.model_validate(response.json())


class TestConfirm:
    """Integration tests for confirm endpoint."""

    @pytest.mark.asyncio
    async def test_confirm_registered_user(
        self,
        test_client: AsyncClient,
        registered_user: UserRow,
        confirmation_token: str,
    ) -> None:
        response = await test_client.get(f"/api/v1/auth/confirm/{confirmation_token}")
        assert response.status_code == 200
        assert BaseResponse.model_validate(response.json())
