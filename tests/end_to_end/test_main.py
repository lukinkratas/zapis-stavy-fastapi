from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient

from api.auth import create_confirmation_token


class TestEndToEnd:
    """End to end test."""

    @pytest.mark.end_to_end
    @pytest.mark.asyncio
    async def test(
        self,
        test_client: AsyncClient,
        creds: dict[str, str],
        update_creds: dict[str, str],
        props: dict[str, str],
        update_props: dict[str, str],
        mock_send_email: MagicMock,
    ) -> None:
        # register user
        response = await test_client.post("/api/v1/auth/register", json=creds)
        assert response.status_code == 201

        # confirm user
        user_id = response.json()["id"]
        confirmation_token = create_confirmation_token(user_id)
        response = await test_client.get(f"/api/v1/auth/confirm/{confirmation_token}")
        assert response.status_code == 200

        # login / get access token
        data = {
            "username": creds["email"],
            "password": creds["password"],  # plain password
        }
        response = await test_client.post(
            "/api/v1/auth/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200

        access_token = response.json()["access_token"]

        # update user
        response = await test_client.put(
            "/api/v1/users/me",
            json=update_creds,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

        # create location
        response = await test_client.post(
            "/api/v1/locations",
            json=props,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 201

        new_location = response.json()
        location_id = new_location["id"]

        # update location
        response = await test_client.put(
            f"/api/v1/locations/{location_id}",
            json=update_props,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

        # delete created location
        response = await test_client.delete(
            f"/api/v1/locations/{location_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

        # delete registered user
        response = await test_client.delete(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
