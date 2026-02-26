"""Temperature 8 Statistics characteristic implementation."""

from __future__ import annotations

import math

import msgspec

from ..constants import SINT8_MAX, SINT8_MIN, UINT8_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_TEMPERATURE_8_RESOLUTION = 0.5  # Temperature 8: M=1, d=0, b=-1 -> 0.5 C
_TIME_EXP_BASE = 1.1
_TIME_EXP_OFFSET = 64


def _decode_time_exponential(raw: int) -> float:
    """Decode Time Exponential 8 raw value to seconds."""
    if raw == 0:
        return 0.0
    return _TIME_EXP_BASE ** (raw - _TIME_EXP_OFFSET)


def _encode_time_exponential(seconds: float) -> int:
    """Encode seconds to Time Exponential 8 raw value."""
    if seconds <= 0.0:
        return 0
    n = round(math.log(seconds) / math.log(_TIME_EXP_BASE) + _TIME_EXP_OFFSET)
    return max(1, min(n, 0xFD))


class Temperature8StatisticsData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for temperature 8 statistics.

    Four temperature values (0.5 C resolution) and a sensing duration
    encoded as Time Exponential 8 (seconds).
    """

    average: float  # Average temperature in C
    standard_deviation: float  # Standard deviation in C
    minimum: float  # Minimum temperature in C
    maximum: float  # Maximum temperature in C
    sensing_duration: float  # Sensing duration in seconds (exponential encoding)

    def __post_init__(self) -> None:
        """Validate data fields."""
        min_temp = SINT8_MIN * _TEMPERATURE_8_RESOLUTION
        max_temp = SINT8_MAX * _TEMPERATURE_8_RESOLUTION
        for name, val in [
            ("average", self.average),
            ("standard_deviation", self.standard_deviation),
            ("minimum", self.minimum),
            ("maximum", self.maximum),
        ]:
            if not min_temp <= val <= max_temp:
                raise ValueError(f"{name} {val} C is outside valid range ({min_temp} to {max_temp})")
        if self.sensing_duration < 0.0:
            raise ValueError(f"Sensing duration {self.sensing_duration} s cannot be negative")


class Temperature8StatisticsCharacteristic(
    BaseCharacteristic[Temperature8StatisticsData],
):
    """Temperature 8 Statistics characteristic (0x2B0F).

    org.bluetooth.characteristic.temperature_8_statistics

    Statistics for Temperature 8 measurements: average, standard deviation,
    minimum, maximum (all sint8, 0.5 C), and sensing duration
    (Time Exponential 8).
    """

    expected_length: int = 5  # 4 x sint8 + uint8
    min_length: int = 5

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> Temperature8StatisticsData:
        """Parse temperature 8 statistics.

        Args:
            data: Raw bytes (5 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            Temperature8StatisticsData.

        """
        avg_raw = DataParser.parse_int8(data, 0, signed=True)
        std_raw = DataParser.parse_int8(data, 1, signed=True)
        min_raw = DataParser.parse_int8(data, 2, signed=True)
        max_raw = DataParser.parse_int8(data, 3, signed=True)
        dur_raw = DataParser.parse_int8(data, 4, signed=False)

        return Temperature8StatisticsData(
            average=avg_raw * _TEMPERATURE_8_RESOLUTION,
            standard_deviation=std_raw * _TEMPERATURE_8_RESOLUTION,
            minimum=min_raw * _TEMPERATURE_8_RESOLUTION,
            maximum=max_raw * _TEMPERATURE_8_RESOLUTION,
            sensing_duration=_decode_time_exponential(dur_raw),
        )

    def _encode_value(self, data: Temperature8StatisticsData) -> bytearray:
        """Encode temperature 8 statistics.

        Args:
            data: Temperature8StatisticsData instance.

        Returns:
            Encoded bytes (5 bytes).

        """
        avg_raw = round(data.average / _TEMPERATURE_8_RESOLUTION)
        std_raw = round(data.standard_deviation / _TEMPERATURE_8_RESOLUTION)
        min_raw = round(data.minimum / _TEMPERATURE_8_RESOLUTION)
        max_raw = round(data.maximum / _TEMPERATURE_8_RESOLUTION)
        dur_raw = _encode_time_exponential(data.sensing_duration)

        for name, value in [
            ("average", avg_raw),
            ("standard_deviation", std_raw),
            ("minimum", min_raw),
            ("maximum", max_raw),
        ]:
            if not SINT8_MIN <= value <= SINT8_MAX:
                raise ValueError(f"{name} raw {value} exceeds sint8 range")
        if not 0 <= dur_raw <= UINT8_MAX:
            raise ValueError(f"Duration raw {dur_raw} exceeds uint8 range")

        result = bytearray()
        result.extend(DataParser.encode_int8(avg_raw, signed=True))
        result.extend(DataParser.encode_int8(std_raw, signed=True))
        result.extend(DataParser.encode_int8(min_raw, signed=True))
        result.extend(DataParser.encode_int8(max_raw, signed=True))
        result.extend(DataParser.encode_int8(dur_raw, signed=False))
        return result
