from typing import Any

from api.models.meters import MeterResponseJson
from api.models.readings import ReadingResponseJson


def assert_meter(meter: dict[str, Any], **kwargs: Any) -> None:
    assert MeterResponseJson.model_validate(meter)
    for key, val in kwargs.items():
        assert meter[key] == val


def assert_reading(reading: dict[str, Any], **kwargs: Any) -> None:
    assert ReadingResponseJson.model_validate(reading)
    for key, val in kwargs.items():
        assert reading[key] == val
