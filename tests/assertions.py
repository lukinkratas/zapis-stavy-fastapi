from typing import Any

from api.schemas.auth import Token
from api.schemas.locations import LocationResponseJson
from api.schemas.users import UserResponseJson


def assert_token(token: dict[str, Any]) -> None:
    assert Token.model_validate(token)


def assert_user(user: dict[str, Any], **kwargs: Any) -> None:
    assert UserResponseJson.model_validate(user)
    for key, val in kwargs.items():
        assert user[key] == val


def assert_location(location: dict[str, Any], **kwargs: Any) -> None:
    assert LocationResponseJson.model_validate(location)
    for key, val in kwargs.items():
        assert location[key] == val
