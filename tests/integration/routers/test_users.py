import pytest
from httpx import AsyncClient
from psycopg import AsyncConnection

from api.repositories.users import UserRow
from api.schemas import BaseResponse
from api.services.users import select_user_by_id


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
            "/api/v1/user", headers={"Authorization": f"Bearer {access_token}"}
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
            "/api/v1/user", headers={"Authorization": f"Bearer {expired_access_token}"}
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
            "/api/v1/user",
            headers={"Authorization": f"Bearer {other_user_access_token}"},
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
            "/api/v1/user",
            headers={"Authorization": f"Bearer {random_user_access_token}"},
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
            "/api/v1/user", headers={"Authorization": f"Bearer {confirmation_token}"}
        )
        assert response.status_code == 401


class TestUpdate:
    """Integration tests for update user endpoint."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_user(
        self,
        test_client: AsyncClient,
        update_creds: dict[str, str],
        registered_user: UserRow,
        access_token: str,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing expected case."""
        user_pre = await select_user_by_id(db_conn, registered_user.id)
        response = await test_client.put(
            "/api/v1/user",
            json=update_creds,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert BaseResponse.model_validate(response.json())

        user_post = await select_user_by_id(db_conn, registered_user.id)
        assert user_pre != user_post, "User was not updated."

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_user_conflict(
        self,
        test_client: AsyncClient,
        update_creds: dict[str, str],
        registered_user: UserRow,
        other_user: UserRow,
        access_token: str,
    ) -> None:
        """Testing expected case."""
        update_creds = {"email": other_user.email}
        response = await test_client.put(
            "/api/v1/user",
            json=update_creds,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_update_user_invalid_schema(
        self,
        test_client: AsyncClient,
        access_token: str,
    ) -> None:
        response = await test_client.put(
            "/api/v1/user",
            json={"username": "update@test.net"},  # username instead of email
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 422

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_user_with_expired_access_token(
        self,
        test_client: AsyncClient,
        update_creds: dict[str, str],
        registered_user: UserRow,
        expired_access_token: str,
    ) -> None:
        """Testing access token with different encoded exp."""
        response = await test_client.put(
            "/api/v1/user",
            json=update_creds,
            headers={"Authorization": f"Bearer {expired_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_user_with_other_user_access_token(
        self,
        test_client: AsyncClient,
        update_creds: dict[str, str],
        registered_user: UserRow,
        other_user_access_token: str,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing access token with different encoded sub."""
        user_pre = await select_user_by_id(db_conn, registered_user.id)

        response = await test_client.put(
            "/api/v1/user",
            json=update_creds,
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
        update_creds: dict[str, str],
        registered_user: UserRow,
        random_user_access_token: str,
    ) -> None:
        """Testing access token with random access token."""
        response = await test_client.put(
            "/api/v1/user",
            json=update_creds,
            headers={"Authorization": f"Bearer {random_user_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_user_with_confirmation_token(
        self,
        test_client: AsyncClient,
        update_creds: dict[str, str],
        registered_user: UserRow,
        confirmation_token: str,
    ) -> None:
        """Testing access token with different encoded typ."""
        response = await test_client.put(
            "/api/v1/user",
            json=update_creds,
            headers={"Authorization": f"Bearer {confirmation_token}"},
        )
        assert response.status_code == 401
