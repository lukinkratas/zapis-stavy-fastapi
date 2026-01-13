from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.db_models.users import UsersTable
from tests.assertions import assert_token


class TestIntegrationAuth:
    """Integration tests for auth."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_login(
        self,
        mocker: MockerFixture,
        async_client: AsyncClient,
        default_user: dict[str, Any],
        hashed_password: str,
    ) -> None:
        default_user_from_db = default_user.copy()
        default_user_from_db["password"] = hashed_password
        mocker.patch.object(
            UsersTable,
            "select_by_email",
            new=AsyncMock(return_value=default_user_from_db),
        )
        request_body = {
            "email": default_user["email"],
            "password": default_user["password"],
        }
        response = await async_client.post("/token", json=request_body)
        assert response.status_code == 200

        token = response.json()
        assert_token(token)
