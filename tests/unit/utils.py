import uuid
from datetime import datetime, timezone
from typing import Any

from api.routers.auth import get_password_hash


def user_factory(credentials: dict[str, str]) -> dict[str, Any]:
    credentials_copy = credentials.copy()
    plain_password = credentials_copy.pop("password")
    credentials_copy["password"] = get_password_hash(plain_password)
    return credentials_copy | {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }


def meter_factory(payload: dict[str, str], user_id: str) -> dict[str, Any]:
    return payload | {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "user_id": user_id,
    }


def reading_factory(payload: dict[str, Any], user_id: str) -> dict[str, Any]:
    return payload | {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "user_id": user_id,
    }
