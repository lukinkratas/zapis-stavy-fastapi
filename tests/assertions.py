from typing import Any

from zapisstavyapi.models import MeterResponseJson, ReadingResponseJson


def assert_meter(meter: MeterResponseJson, **kwargs: Any) -> None:
    assert MeterResponseJson.model_validate(meter)
    for key, val in kwargs.items():
        assert meter[key] == val


def assert_reading(reading: ReadingResponseJson, **kwargs: Any) -> None:
    assert ReadingResponseJson.model_validate(reading)
    for key, val in kwargs.items():
        assert reading[key] == val
