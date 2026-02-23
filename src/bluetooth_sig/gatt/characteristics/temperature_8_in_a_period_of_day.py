"""Temperature 8 in a Period of Day characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import SINT8_MAX, SINT8_MIN, UINT8_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_TEMPERATURE_8_RESOLUTION = 0.5  # Temperature 8: M=1, d=0, b=-1 -> 0.5 C
_TIME_DECIHOUR_RESOLUTION = 0.1  # Time Decihour 8: M=1, d=-1, b=0 -> 0.1 hr


class Temperature8InAPeriodOfDayData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for temperature 8 in a period of day.

    Temperature in degrees Celsius (0.5 C resolution) with a
    time-of-day range (0.1 hr resolution).
    """

    temperature: float  # Temperature in C (0.5 C resolution)
    start_time: float  # Start time in hours (0.1 hr resolution)
    end_time: float  # End time in hours (0.1 hr resolution)

    def __post_init__(self) -> None:
        """Validate data fields."""
        min_temp = SINT8_MIN * _TEMPERATURE_8_RESOLUTION
        max_temp = SINT8_MAX * _TEMPERATURE_8_RESOLUTION
        if not min_temp <= self.temperature <= max_temp:
            raise ValueError(f"Temperature {self.temperature} C is outside valid range ({min_temp} to {max_temp})")
        max_time = UINT8_MAX * _TIME_DECIHOUR_RESOLUTION
        for name, val in [("start_time", self.start_time), ("end_time", self.end_time)]:
            if not 0.0 <= val <= max_time:
                raise ValueError(f"{name} {val} hr is outside valid range (0.0 to {max_time})")


class Temperature8InAPeriodOfDayCharacteristic(
    BaseCharacteristic[Temperature8InAPeriodOfDayData],
):
    """Temperature 8 in a Period of Day characteristic (0x2B0E).

    org.bluetooth.characteristic.temperature_8_in_a_period_of_day

    Represents a temperature reading within a time-of-day range. Fields:
    Temperature 8 (sint8, 0.5 C), start time (uint8, 0.1 hr),
    end time (uint8, 0.1 hr).
    """

    expected_length: int = 3  # sint8 + 2 x uint8
    min_length: int = 3

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> Temperature8InAPeriodOfDayData:
        """Parse temperature 8 in a period of day.

        Args:
            data: Raw bytes (3 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            Temperature8InAPeriodOfDayData.

        """
        temp_raw = DataParser.parse_int8(data, 0, signed=True)
        start_raw = DataParser.parse_int8(data, 1, signed=False)
        end_raw = DataParser.parse_int8(data, 2, signed=False)

        return Temperature8InAPeriodOfDayData(
            temperature=temp_raw * _TEMPERATURE_8_RESOLUTION,
            start_time=start_raw * _TIME_DECIHOUR_RESOLUTION,
            end_time=end_raw * _TIME_DECIHOUR_RESOLUTION,
        )

    def _encode_value(self, data: Temperature8InAPeriodOfDayData) -> bytearray:
        """Encode temperature 8 in a period of day.

        Args:
            data: Temperature8InAPeriodOfDayData instance.

        Returns:
            Encoded bytes (3 bytes).

        """
        temp_raw = round(data.temperature / _TEMPERATURE_8_RESOLUTION)
        start_raw = round(data.start_time / _TIME_DECIHOUR_RESOLUTION)
        end_raw = round(data.end_time / _TIME_DECIHOUR_RESOLUTION)

        if not SINT8_MIN <= temp_raw <= SINT8_MAX:
            raise ValueError(f"Temperature raw {temp_raw} exceeds sint8 range")
        for name, value in [("start_time", start_raw), ("end_time", end_raw)]:
            if not 0 <= value <= UINT8_MAX:
                raise ValueError(f"{name} raw value {value} exceeds uint8 range")

        result = bytearray()
        result.extend(DataParser.encode_int8(temp_raw, signed=True))
        result.extend(DataParser.encode_int8(start_raw, signed=False))
        result.extend(DataParser.encode_int8(end_raw, signed=False))
        return result
