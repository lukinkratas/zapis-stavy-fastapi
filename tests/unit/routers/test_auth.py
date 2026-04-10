from typing import Any
from unittest.mock import AsyncMock

import jwt
import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.config import settings
from api.models.users import UsersTable
from tests.assertions import assert_token


class TestUnitAuth:
    """Unit tests for auth."""

    @pytest.mark.anyio
    async def test_login(
        self,
        mocker: MockerFixture,
        async_client: AsyncClient,
        credentials: dict[str, str],
        registered_user: dict[str, Any],
    ) -> None:
        # mocking - returns user from db with hashed password
        mocker.patch.object(
            UsersTable,
            "select_by_email",
            new=AsyncMock(return_value=registered_user),
        )

        data = {
            "username": credentials["email"],
            "password": credentials["password"],  # plain password
        }
        response = await async_client.post("/token", data=data)
        assert response.status_code == 200

        token = response.json()
        assert_token(token)
