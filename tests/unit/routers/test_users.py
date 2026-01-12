from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.db_models.users import UsersTable
from tests.assertions import assert_user


class TestIntegrationUser:
    """Integration tests for users."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_register_and_delete_user(
        self,
        async_client: AsyncClient,
        mocker: MockerFixture,
        default_user: dict[str, Any],
    ) -> None:
        # register user
        mocker.patch.object(
            UsersTable, "insert", new=AsyncMock(return_value=default_user)
        )
        request_body = {"email": "integration@test.net", "password": "123456seven"}
        response = await async_client.post("/register", json=request_body)
        assert response.status_code == 201

        new_user = response.json()
        assert_user(new_user)

        # delete registered user
        mocker.patch.object(UsersTable, "delete", new=AsyncMock(return_value=None))
        uid = new_user["id"]
        response = await async_client.delete(f"/user/{uid}")
        assert response.status_code == 200
