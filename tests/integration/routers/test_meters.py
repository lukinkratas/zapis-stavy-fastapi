from typing import Any

import pytest
from httpx import AsyncClient

from tests.assertions import assert_meter


class TestIntegrationMeter:
    """Integration tests for meters."""

    @pytest.fixture
    def create_request_body(self) -> dict[str, str]:
        return {"name": "new"}

    @pytest.fixture
    def update_request_body(self) -> dict[str, str]:
        return {"name": "update"}

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_and_delete_meter(
        self,
        async_client: AsyncClient,
        token: str,
        create_request_body: dict[str, str],
    ) -> None:
        # create meter
        response = await async_client.post(
            "/meter",
            json=create_request_body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

        new_meter = response.json()
        assert_meter(new_meter, **create_request_body)

        # delete created meter
        mid = new_meter["id"]
        response = await async_client.delete(
            f"/meter/{mid}", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_existing_meter(
        self,
        async_client: AsyncClient,
        token: str,
        created_meter: dict[str, Any],
    ) -> None:
        # requires meter to be already created
        create_request_body = {"name": created_meter["name"]}
        response = await async_client.post(
            "/meter",
            json=create_request_body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 409

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_meter_not_registered_email_token(
        self,
        async_client: AsyncClient,
        not_registered_email_token: str,
        create_request_body: dict[str, str],
    ) -> None:
        response = await async_client.post(
            "/meter",
            json=create_request_body,
            headers={"Authorization": f"Bearer {not_registered_email_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_meter_expired_token(
        self,
        async_client: AsyncClient,
        expired_token: str,
        create_request_body={"name": "new"},
    ) -> None:
        response = await async_client.post(
            "/meter",
            json=create_request_body,
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_delete_non_existing_meter(
        self,
        async_client: AsyncClient,
        random_uuid: str,
        token: str,
    ) -> None:
        response = await async_client.delete(
            f"/meter/{random_uuid}", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_meter(
        self,
        async_client: AsyncClient,
        created_meter: dict[str, Any],
        update_request_body: dict[str, str],
        token: str,
    ) -> None:
        mid = created_meter["id"]
        response = await async_client.put(
            f"/meter/{mid}",
            json=update_request_body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        updated_meter = response.json()
        assert_meter(updated_meter, **update_request_body)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_non_existing_meter(
        self,
        async_client: AsyncClient,
        random_uuid: str,
        update_request_body: dict[str, str],
        token: str,
    ) -> None:
        response = await async_client.put(
            f"/meter/{random_uuid}",
            json=update_request_body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_readings_on_meter(
        self,
        async_client: AsyncClient,
        created_meter: dict[str, Any],
        created_reading: dict[str, Any],
        token: str,
    ) -> None:
        mid = created_meter["id"]
        response = await async_client.get(
            f"/meter/{mid}/reading", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        readings = response.json()
        assert created_reading in readings

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_meter_with_readings(
        self,
        async_client: AsyncClient,
        created_meter: dict[str, Any],
        created_reading: dict[str, Any],
        token: str,
    ) -> None:
        mid = created_meter["id"]
        response = await async_client.get(
            f"/meter/{mid}", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        meter_with_readings = response.json()
        assert meter_with_readings == {
            "meter": created_meter,
            "readings": [created_reading],
        }

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_non_existing_meter_with_readings(
        self, async_client: AsyncClient, random_uuid: str, token: str
    ) -> None:
        response = await async_client.get(
            f"/meter/{random_uuid}", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404
