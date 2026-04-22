import uuid
from datetime import datetime, timezone
from typing import Any
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.models.users import UsersTable
from api.routers.auth import get_password_hash
from api.schemas.users import UserResponseJson


class TestUnitUser:
    """Integration tests for users."""

    @pytest.mark.anyio
    async def test_register_user(
        self,
        async_client: AsyncClient,
        mocker: MockerFixture,
        credentials: dict[str, str],
        registered_user_json: dict[str, Any],
        mock_send_email: MagicMock,
    ) -> None:
        # mock
        mocker.patch.object(UsersTable, "insert", return_value=registered_user_json)

        # register user
        response = await async_client.post("/register", json=credentials)
        assert response.status_code == 201
        mock_send_email.assert_called_once()

        registered_user = response.json()["user"]
        assert UserResponseJson.model_validate(registered_user)

    @pytest.mark.parametrize(
        "credentials",
        [
            pytest.param({"email": "test@test.net"}, id="missing password"),
            pytest.param({"password": "password"}, id="missing email"),
            pytest.param(
                {"username": "test@test.net", "password": "password"},
                id="username instead of email",
            ),
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
    async def test_delete_user(
        self,
        async_client: AsyncClient,
        mocker: MockerFixture,
        registered_user: dict[str, Any],
        access_token: str,
    ) -> None:
        # mock
        mocker.patch.object(UsersTable, "delete", return_value=None)

        # delete registered user
        response = await async_client.delete(
            "/user", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.anyio
    async def test_update_user(
        self,
        mocker: MockerFixture,
        async_client: AsyncClient,
        update_user_payload: dict[str, str],
        registered_user: dict[str, Any],
        access_token: str,
    ) -> None:
        updated_user_from_db = {
            "email": update_user_payload["email"],
            "password": get_password_hash(update_user_payload["password"]),
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }

        # mock
        mocker.patch.object(UsersTable, "update", return_value=updated_user_from_db)

        # update user
        response = await async_client.put(
            "/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

        updated_user = response.json()
        assert UserResponseJson.model_validate(updated_user)
