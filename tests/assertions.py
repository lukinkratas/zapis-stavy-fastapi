from typing import Any

from api.schemas.auth import Token
from api.schemas.meters import MeterResponseJson
from api.schemas.readings import ReadingResponseJson
from api.schemas.users import UserResponseJson


def assert_token(token: dict[str, Any]) -> None:
    assert Token.model_validate(token)


def assert_user(user: dict[str, Any], **kwargs: Any) -> None:
    assert UserResponseJson.model_validate(user)
    for key, val in kwargs.items():
        assert user[key] == val


def assert_meter(meter: dict[str, Any], **kwargs: Any) -> None:
    assert MeterResponseJson.model_validate(meter)
    for key, val in kwargs.items():
        assert meter[key] == val


def assert_reading(reading: dict[str, Any], **kwargs: Any) -> None:
    assert ReadingResponseJson.model_validate(reading)
    for key, val in kwargs.items():
        assert reading[key] == val
