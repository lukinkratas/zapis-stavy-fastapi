from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.models.users import UsersTable
from tests.assertions import assert_user

from ..utils import user_factory


class TestUnitUser:
    """Integration tests for users."""

    @pytest.mark.anyio
    async def test_register_and_delete_user(
        self,
        async_client: AsyncClient,
        mocker: MockerFixture,
    ) -> None:
        credentials = {"email": "register@register.net", "password": "123456seven"}

        # mocking
        new_user = user_factory(credentials)
        mocker.patch.object(UsersTable, "insert", new=AsyncMock(return_value=new_user))

        # register user
        response = await async_client.post("/register", json=credentials)
        assert response.status_code == 201

        new_user = response.json()
        assert_user(new_user)

        # delete registered user
        mocker.patch.object(UsersTable, "delete", new=AsyncMock(return_value=None))
        uid = new_user["id"]
        response = await async_client.delete(f"/user/{uid}")
        assert response.status_code == 204

    @pytest.mark.parametrize(
        "credentials",
        [
            {"username": "register@register.net", "password": "123456seven"},
            {"password": "123456seven"},
            {"email": "register@register.net"},
        ],
    )
    @pytest.mark.anyio
    async def test_register_invalid_schema(
        self, async_client: AsyncClient, credentials: dict[str, str]
    ) -> None:
        # register user
        response = await async_client.post("/register", json=credentials)
        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_update_user(
        self,
        mocker: MockerFixture,
        async_client: AsyncClient,
        registered_user: dict[str, Any],
    ) -> None:
        updated_credentials = {"email": "update@update.net", "password": "5six7"}

        # mocking
        updated_user = user_factory(updated_credentials)
        mocker.patch.object(
            UsersTable, "update", new=AsyncMock(return_value=updated_user)
        )

        # update registered user
        uid = registered_user["id"]
        response = await async_client.put(f"/user/{uid}", json=updated_credentials)
        assert response.status_code == 200

        updated_user = response.json()
        assert_user(updated_user)
