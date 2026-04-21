import uuid
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.models.users import UsersTable
from api.routers.auth import get_password_hash
from api.schemas.users import UserResponseJson


class TestUnitUser:
    """Integration tests for users."""

    @pytest.fixture
    def mock_send_email(self, mocker: MockerFixture) -> MockerFixture:
        """Prevent real SES calls in all integration tests."""
        return mocker.patch(
            "api.routers.users.ses_send_email",
            return_value={
                "MessageId": "EXAMPLE78603177f-7a5433e7-8edb-42ae-af10-f0181f34d6ee",
                "ResponseMetadata": {},
            },
        )

    @pytest.mark.anyio
    async def test_register_and_delete_user(
        self,
        async_client: AsyncClient,
        mocker: MockerFixture,
        credentials: dict[str, str],
        registered_user_from_db: dict[str, Any],
        mock_send_email: MockerFixture,
        access_token: str,
    ) -> None:
        # mock
        mocker.patch.object(
            UsersTable, "insert", new=AsyncMock(return_value=registered_user_from_db)
        )

        # register user
        response = await async_client.post("/register", json=credentials)
        assert response.status_code == 201
        mock_send_email.assert_called_once()

        registered_user = response.json()["user"]
        assert UserResponseJson.model_validate(registered_user)

        # mock
        mocker.patch.object(
            UsersTable,
            "select_by_id",
            new=AsyncMock(return_value=registered_user_from_db),
        )
        mocker.patch.object(UsersTable, "delete", new=AsyncMock(return_value=None))

        # delete registered user
        response = await async_client.delete(
            "/user", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "credentials",
        [
            {"email": "test@test.net"},
            {"password": "password"},
            {"username": "test@test.net", "password": "password"},
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
        registered_user_from_db: dict[str, Any],
        update_user_payload: dict[str, str],
        access_token: str,
    ) -> None:
        updated_user_from_db = {
            "email": update_user_payload["email"],
            "password": get_password_hash(update_user_payload["password"]),
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }

        # mock
        mocker.patch.object(
            UsersTable,
            "select_by_id",
            new=AsyncMock(return_value=registered_user_from_db),
        )
        mocker.patch.object(
            UsersTable, "update", new=AsyncMock(return_value=updated_user_from_db)
        )

        # update user
        response = await async_client.put(
            "/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

        updated_user = response.json()
        assert UserResponseJson.model_validate(updated_user)
