import os
from pathlib import Path
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from pytest_mock import MockerFixture
from testcontainers.postgres import PostgresContainer

from api.main import app
from api.routers.auth import create_confirmation_token

ROOT = Path(__file__).parent.parent.parent.resolve()


class TestEndToEnd:
    """End to end test."""

    @pytest.fixture(scope="session")
    def anyio_backend(self) -> str:
        return "asyncio"

    @pytest.fixture(scope="session")
    async def async_client(self) -> AsyncGenerator[AsyncClient, None]:
        app.state.limiter.enabled = False

        with (
            PostgresContainer("postgres:14")
            .with_volume_mapping(
                str(ROOT / "scripts/init-db.sh"),
                "/docker-entrypoint-initdb.d/init-db.sh",
            )
            .with_volume_mapping(
                str(ROOT / "sql/"), "/docker-entrypoint-initdb.d/sql/"
            ) as postgres
        ):
            os.environ["DB_NAME"] = postgres.dbname
            os.environ["DB_USERNAME"] = postgres.username
            os.environ["DB_PASSWORD"] = postgres.password
            os.environ["DB_PORT"] = str(postgres.get_exposed_port(5432))
            os.environ["DB_HOST"] = postgres.get_container_host_ip()

            async with app.router.lifespan_context(app):
                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                ) as async_client:
                    yield async_client

    @pytest.fixture
    def mock_send_email(self, mocker: MockerFixture) -> MockerFixture:
        return mocker.patch(
            "api.routers.users.ses_send_email",
            return_value={
                "MessageId": "EXAMPLE78603177f-7a5433e7-8edb-42ae-af10-f0181f34d6ee",
                "ResponseMetadata": {},
            },
        )

    @pytest.mark.end_to_end
    @pytest.mark.anyio
    async def test(
        self,
        async_client: AsyncClient,
        credentials: dict[str, str],
        update_user_payload: dict[str, str],
        location_payload: dict[str, str],
        update_location_payload: dict[str, str],
        mock_send_email: MockerFixture,
    ) -> None:
        # register user
        credentials = {"email": "test@test.net", "password": "password"}
        response = await async_client.post("/register", json=credentials)
        assert response.status_code == 201

        registered_user = response.json()["user"]
        user_id = registered_user["id"]

        # confirm user
        confirmation_token = create_confirmation_token(user_id)
        response = await async_client.get(f"/confirm/{confirmation_token}")
        assert response.status_code == 200

        # login / get access token
        data = {
            "username": credentials["email"],
            "password": credentials["password"],  # plain password
        }
        response = await async_client.post(
            "/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200

        access_token = response.json()["access_token"]

        # update user
        response = await async_client.put(
            "/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

        # create location
        response = await async_client.post(
            "/location",
            json=location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 201

        new_location = response.json()
        location_id = new_location["id"]

        # update location
        response = await async_client.put(
            f"/location/{location_id}",
            json=update_location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

        # delete created location
        response = await async_client.delete(
            f"/location/{location_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

        # delete registered user
        response = await async_client.delete(
            "/user", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
