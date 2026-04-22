import uuid
from datetime import timedelta
from typing import Any
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from api.routers.auth import create_access_token, create_confirmation_token


@pytest.fixture
def mock_send_email(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "api.routers.users.ses_send_email",
        return_value={
            "MessageId": "EXAMPLE78603177f-7a5433e7-8edb-42ae-af10-f0181f34d6ee-000000",
            "ResponseMetadata": {},
        },
    )


@pytest.fixture
def credentials() -> dict[str, str]:
    return {"email": "test@test.net", "password": "password"}


@pytest.fixture
def update_user_payload() -> dict[str, str]:
    return {"email": "update@test.net", "password": "update"}


@pytest.fixture
def location_payload() -> dict[str, str]:
    return {"name": "test"}


@pytest.fixture
def update_location_payload() -> dict[str, str]:
    return {"name": "update"}


@pytest.fixture
def user_id(registered_user: dict[str, Any]) -> str:
    return registered_user["id"]


@pytest.fixture
async def access_token(user_id: str) -> str:
    return create_access_token(user_id)


@pytest.fixture
async def confirmation_token(user_id: str) -> str:
    return create_confirmation_token(user_id)


@pytest.fixture
async def expired_access_token(user_id: str) -> str:
    return create_access_token(user_id, expires_delta=timedelta(-1))


@pytest.fixture
async def expired_confirmation_token(user_id: str) -> str:
    return create_confirmation_token(user_id, expires_delta=timedelta(-1))


@pytest.fixture
def random_id_access_token() -> str:
    return create_access_token(str(uuid.uuid4()))
