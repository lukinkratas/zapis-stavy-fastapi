import pytest
from httpx import AsyncClient

from api.routers.auth import verify_password
from tests.assertions import assert_user


class TestIntegrationUser:
    """Integration tests for users."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_register_and_delete_user(self, async_client: AsyncClient) -> None:
        # register user
        request_body = {"email": "integration@test.net", "password": "123456seven"}
        response = await async_client.post("/register", json=request_body)
        assert response.status_code == 201

        new_user = response.json()
        # pop password, cause it is hashed
        password = request_body.pop("password")
        assert verify_password(password, new_user["password"])
        assert_user(new_user, **request_body)

        # delete registered user
        uid = new_user["id"]
        response = await async_client.delete(f"/user/{uid}")
        assert response.status_code == 200
