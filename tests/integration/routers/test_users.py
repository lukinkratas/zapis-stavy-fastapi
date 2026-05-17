from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient
from psycopg import AsyncConnection

from api.repositories.users import UserRow
from api.schemas import BaseResponse, ResponseWithId
from api.services.users import delete_user, select_user_by_id


class TestRegister:
    """Integration tests for create user endpoints."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_register_user(
        self,
        test_client: AsyncClient,
        creds: dict[str, str],
        mock_send_email: MagicMock,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing expected case."""
        response = await test_client.post("/v1/user/register", json=creds)
        assert response.status_code == 201
        mock_send_email.assert_called_once()
        assert ResponseWithId.model_validate(response.json())

        user_id = response.json()["id"]
        user = await select_user_by_id(db_conn, user_id)
        assert user is not None, "User does not exist in db."

        # clean-up
        await delete_user(db_conn, user.id)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_register_already_registered_user(
        self,
        test_client: AsyncClient,
        creds: dict[str, str],
        registered_user: UserRow,
    ) -> None:
        response = await test_client.post("/v1/user/register", json=creds)
        assert response.status_code == 409

    @pytest.mark.parametrize(
        "creds",
        [
            pytest.param({"email": "test@test.net"}, id="missing password"),
            pytest.param({"password": "password"}, id="missing email"),
            pytest.param(
                {"username": "test@test.net", "password": "password"},
                id="username instead of email",
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_register_invalid_schema(
        self, test_client: AsyncClient, creds: dict[str, str]
    ) -> None:
        response = await test_client.post("/v1/user/register", json=creds)
        assert response.status_code == 422


class TestDelete:
    """Integration tests for delete user endpoints."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_user(
        self,
        test_client: AsyncClient,
        registered_user: UserRow,
        access_token: str,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing expected case."""
        response = await test_client.delete(
            "/v1/user", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        assert BaseResponse.model_validate(response.json())

        user_from_db = await select_user_by_id(db_conn, registered_user.id)
        assert user_from_db is None, "User still exists in db."

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_user_with_expired_access_token(
        self,
        test_client: AsyncClient,
        registered_user: UserRow,
        expired_access_token: str,
    ) -> None:
        """Testing access token with different encoded exp."""
        response = await test_client.delete(
            "/v1/user", headers={"Authorization": f"Bearer {expired_access_token}"}
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_user_with_other_user_access_token(
        self,
        test_client: AsyncClient,
        registered_user: UserRow,
        other_user: UserRow,
        other_user_access_token: str,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing access token with different encoded sub."""
        registered_user_from_db = await select_user_by_id(db_conn, registered_user.id)
        assert registered_user_from_db is not None, "User does not exist in db."
        other_confirmed_user_from_db = await select_user_by_id(db_conn, other_user.id)
        assert other_confirmed_user_from_db is not None, (
            "Other user does not exist in db."
        )

        response = await test_client.delete(
            "/v1/user", headers={"Authorization": f"Bearer {other_user_access_token}"}
        )
        assert response.status_code == 200

        registered_user_from_db = await select_user_by_id(db_conn, registered_user.id)
        assert registered_user_from_db is not None, "User was deleted by other user."
        other_confirmed_user_from_db = await select_user_by_id(db_conn, other_user.id)
        assert other_confirmed_user_from_db is None, "Other user was not deleted"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_user_with_random_user_access_token(
        self,
        test_client: AsyncClient,
        registered_user: UserRow,
        random_user_access_token: str,
    ) -> None:
        """Testing access token with random access token."""
        response = await test_client.delete(
            "/v1/user", headers={"Authorization": f"Bearer {random_user_access_token}"}
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_user_with_confirmation_token(
        self,
        test_client: AsyncClient,
        registered_user: UserRow,
        confirmation_token: str,
    ) -> None:
        """Testing access token with different encoded typ."""
        response = await test_client.delete(
            "/v1/user", headers={"Authorization": f"Bearer {confirmation_token}"}
        )
        assert response.status_code == 401


class TestUpdate:
    """Integration tests for update user endpoint."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_user(
        self,
        test_client: AsyncClient,
        update_user_payload: dict[str, str],
        registered_user: UserRow,
        access_token: str,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing expected case."""
        user_pre = await select_user_by_id(db_conn, registered_user.id)
        response = await test_client.put(
            "/v1/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert BaseResponse.model_validate(response.json())

        user_post = await select_user_by_id(db_conn, registered_user.id)
        assert user_pre != user_post, "User was not updated"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_user_with_expired_access_token(
        self,
        test_client: AsyncClient,
        update_user_payload: dict[str, str],
        registered_user: UserRow,
        expired_access_token: str,
    ) -> None:
        """Testing access token with different encoded exp."""
        response = await test_client.put(
            "/v1/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {expired_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_user_with_other_user_access_token(
        self,
        test_client: AsyncClient,
        update_user_payload: dict[str, str],
        registered_user: UserRow,
        other_user_access_token: str,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing access token with different encoded sub."""
        user_pre = await select_user_by_id(db_conn, registered_user.id)

        response = await test_client.put(
            "/v1/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {other_user_access_token}"},
        )

        assert response.status_code == 200
        user_post = await select_user_by_id(db_conn, registered_user.id)
        assert user_pre == user_post, "User was updated by other user."

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_user_with_random_user_access_token(
        self,
        test_client: AsyncClient,
        update_user_payload: dict[str, str],
        registered_user: UserRow,
        random_user_access_token: str,
    ) -> None:
        """Testing access token with random access token."""
        response = await test_client.put(
            "/v1/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {random_user_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_user_with_confirmation_token(
        self,
        test_client: AsyncClient,
        update_user_payload: dict[str, str],
        registered_user: UserRow,
        confirmation_token: str,
    ) -> None:
        """Testing access token with different encoded typ."""
        response = await test_client.put(
            "/v1/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {confirmation_token}"},
        )
        assert response.status_code == 401
