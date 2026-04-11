from typing import Any

import jwt
import pytest

from api.auth import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_confirmation_token,
    verify_password,
)


class TestUnitAuth:
    """Unit tests for auth."""

    @pytest.mark.anyio
    async def test_verify_password(
        self,
        credentials: dict[str, str],
        registered_user: dict[str, Any],
    ) -> None:
        verify_password(credentials["password"], registered_user["password"])

    @pytest.mark.anyio
    async def test_create_access_token(
        self,
        credentials: dict[str, str],
    ) -> None:
        token = create_access_token(credentials["email"])
        decoded_token = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded_token["sub"] == credentials["email"]
        assert decoded_token["type"] == "access"

    @pytest.mark.anyio
    async def test_create_confirmation_token(
        self,
        credentials: dict[str, str],
    ) -> None:
        token = create_confirmation_token(credentials["email"])
        decoded_token = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded_token["sub"] == credentials["email"]
        assert decoded_token["type"] == "confirmation"
