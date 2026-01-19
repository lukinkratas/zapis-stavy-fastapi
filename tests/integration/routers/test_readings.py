from typing import Any

import pytest
from httpx import AsyncClient

from tests.assertions import assert_reading


class TestIntegrationReading:
    """Integration tests for readings."""

    @pytest.fixture
    def create_request_body(self, created_meter: dict[str, Any]) -> dict[str, Any]:
        return {"meter_id": created_meter["id"], "value": 99.0}

    @pytest.fixture
    def update_request_body(self) -> dict[str, Any]:
        return {"value": 55.0}

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_and_delete_reading(
        self,
        async_client: AsyncClient,
        created_meter: dict[str, Any],
        token: str,
        create_request_body: dict[str, Any],
    ) -> None:
        # create reading
        response = await async_client.post(
            "/reading",
            json=create_request_body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

        new_reading = response.json()
        assert_reading(new_reading, **create_request_body)

        # delete created reading
        rid = new_reading["id"]
        response = await async_client.delete(
            f"/reading/{rid}", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_reading_not_registered_email_token(
        self,
        async_client: AsyncClient,
        created_meter: dict[str, Any],
        not_registered_email_token: str,
        create_request_body: dict[str, Any],
    ) -> None:
        response = await async_client.post(
            "/reading",
            json=create_request_body,
            headers={"Authorization": f"Bearer {not_registered_email_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_reading_expired_token(
        self,
        async_client: AsyncClient,
        created_meter: dict[str, Any],
        expired_token: str,
        create_request_body: dict[str, Any],
    ) -> None:
        response = await async_client.post(
            "/reading",
            json=create_request_body,
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_delete_non_existing_reading(
        self, async_client: AsyncClient, random_uuid: str, token: str
    ) -> None:
        response = await async_client.delete(
            f"/reading/{random_uuid}", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_reading(
        self,
        async_client: AsyncClient,
        created_reading: dict[str, Any],
        update_request_body: dict[str, Any],
        token: str,
    ) -> None:
        rid = created_reading["id"]
        response = await async_client.put(
            f"/reading/{rid}",
            json=update_request_body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        updated_reading = response.json()
        assert_reading(updated_reading, **update_request_body)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_non_existing_reading(
        self,
        async_client: AsyncClient,
        random_uuid: str,
        update_request_body: dict[str, Any],
        token: str,
    ) -> None:
        response = await async_client.put(
            f"/reading/{random_uuid}",
            json=update_request_body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
