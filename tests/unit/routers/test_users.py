import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient

from api.repositories.users import UserRow, UsersTable
from api.schemas import BaseResponse, ResponseWithId
from api.security import get_password_hash


class TestRegister:
    """Integration tests for create user endpoints."""

    @pytest.mark.asyncio
    async def test_register_user(
        self,
        test_client: AsyncClient,
        creds: dict[str, str],
        registered_user_row: UserRow,
        mock_send_email: MagicMock,
    ) -> None:
        # mock
        with patch.object(UsersTable, "insert", return_value=registered_user_row):
            # register user
            response = await test_client.post("/api/v1/user/register", json=creds)

        assert response.status_code == 201
        assert ResponseWithId.model_validate(response.json())
        mock_send_email.assert_called_once()


class TestDelete:
    """Integration tests for delete user endpoints."""

    @pytest.mark.asyncio
    async def test_delete_user(
        self,
        test_client: AsyncClient,
        registered_user_row: UserRow,
        access_token: str,
    ) -> None:
        # mock
        with patch.object(UsersTable, "delete", return_value=registered_user_row):
            # delete registered user
            response = await test_client.delete(
                "/api/v1/user", headers={"Authorization": f"Bearer {access_token}"}
            )

        assert response.status_code == 200
        assert BaseResponse.model_validate(response.json())


class TestUpdate:
    """Integration tests for update user endpoint."""

    @pytest.mark.asyncio
    async def test_update_user(
        self,
        test_client: AsyncClient,
        update_creds: dict[str, str],
        registered_user_row: UserRow,
        access_token: str,
    ) -> None:
        updated_user_from_db = {
            "email": update_creds.get("email") or registered_user_row.email,
            "password_hash": get_password_hash(update_creds["password"])
            if update_creds.get("password") is not None
            else registered_user_row.password_hash,
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }

        # mock
        with patch.object(UsersTable, "update", return_value=updated_user_from_db):
            # update user
            response = await test_client.put(
                "/api/v1/user",
                json=update_creds,
                headers={"Authorization": f"Bearer {access_token}"},
            )

        assert response.status_code == 200
        assert BaseResponse.model_validate(response.json())
