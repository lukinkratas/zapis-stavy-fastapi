import uuid
from datetime import datetime, timezone
from typing import Any
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.models.users import UsersTable
from api.schemas import BaseResponse, ResponseWithId
from api.security import get_password_hash


class TestRegister:
    """Integration tests for create user endpoints."""

    @pytest.mark.asyncio
    async def test_register_user(
        self,
        test_client: AsyncClient,
        mocker: MockerFixture,
        creds: dict[str, str],
        registered_user_from_db: dict[str, Any],
        mock_send_email: MagicMock,
    ) -> None:
        # mock
        mocker.patch.object(UsersTable, "insert", return_value=registered_user_from_db)

        # register user
        response = await test_client.post("/v1/user/register", json=creds)
        assert response.status_code == 201
        assert ResponseWithId.model_validate(response.json())
        mock_send_email.assert_called_once()


class TestDelete:
    """Integration tests for delete user endpoints."""

    @pytest.mark.asyncio
    async def test_delete_user(
        self,
        test_client: AsyncClient,
        mocker: MockerFixture,
        registered_user_from_db: dict[str, Any],
        access_token: str,
    ) -> None:
        # mock
        mocker.patch.object(UsersTable, "delete", return_value=registered_user_from_db)

        # delete registered user
        response = await test_client.delete(
            "/v1/user", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        assert BaseResponse.model_validate(response.json())


class TestUpdate:
    """Integration tests for update user endpoint."""

    @pytest.mark.asyncio
    async def test_update_user(
        self,
        mocker: MockerFixture,
        test_client: AsyncClient,
        update_user_payload: dict[str, str],
        registered_user_from_db: dict[str, Any],
        access_token: str,
    ) -> None:
        updated_user_from_db = {
            "email": update_user_payload.get("email")
            or registered_user_from_db["email"],
            "password_hash": get_password_hash(update_user_payload["password"])
            if update_user_payload.get("password") is not None
            else registered_user_from_db["password_hash"],
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }

        # mock
        mocker.patch.object(UsersTable, "update", return_value=updated_user_from_db)

        # update user
        response = await test_client.put(
            "/v1/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert BaseResponse.model_validate(response.json())
