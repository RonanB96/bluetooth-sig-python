"""Temperature Statistics characteristic implementation."""

from __future__ import annotations

import math

import msgspec

from ..constants import SINT16_MAX, SINT16_MIN, TEMPERATURE_RESOLUTION, UINT8_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

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


class TemperatureStatisticsData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for temperature statistics.

    Four temperature values (0.01 C resolution) and a sensing duration
    encoded as Time Exponential 8 (seconds).
    """

    average: float  # Average temperature in C
    standard_deviation: float  # Standard deviation in C
    minimum: float  # Minimum temperature in C
    maximum: float  # Maximum temperature in C
    sensing_duration: float  # Sensing duration in seconds (exponential encoding)

    def __post_init__(self) -> None:
        """Validate data fields."""
        min_temp = SINT16_MIN * TEMPERATURE_RESOLUTION
        max_temp = SINT16_MAX * TEMPERATURE_RESOLUTION
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


class TemperatureStatisticsCharacteristic(
    BaseCharacteristic[TemperatureStatisticsData],
):
    """Temperature Statistics characteristic (0x2B11).

    org.bluetooth.characteristic.temperature_statistics

    Statistics for Temperature measurements: average, standard deviation,
    minimum, maximum (all sint16, 0.01 C), and sensing duration
    (Time Exponential 8).
    """

    expected_length: int = 9  # 4 x sint16 + uint8
    min_length: int = 9

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> TemperatureStatisticsData:
        """Parse temperature statistics.

        Args:
            data: Raw bytes (9 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            TemperatureStatisticsData.

        """
        avg_raw = DataParser.parse_int16(data, 0, signed=True)
        std_raw = DataParser.parse_int16(data, 2, signed=True)
        min_raw = DataParser.parse_int16(data, 4, signed=True)
        max_raw = DataParser.parse_int16(data, 6, signed=True)
        dur_raw = DataParser.parse_int8(data, 8, signed=False)

        return TemperatureStatisticsData(
            average=avg_raw * TEMPERATURE_RESOLUTION,
            standard_deviation=std_raw * TEMPERATURE_RESOLUTION,
            minimum=min_raw * TEMPERATURE_RESOLUTION,
            maximum=max_raw * TEMPERATURE_RESOLUTION,
            sensing_duration=_decode_time_exponential(dur_raw),
        )

    def _encode_value(self, data: TemperatureStatisticsData) -> bytearray:
        """Encode temperature statistics.

        Args:
            data: TemperatureStatisticsData instance.

        Returns:
            Encoded bytes (9 bytes).

        """
        avg_raw = round(data.average / TEMPERATURE_RESOLUTION)
        std_raw = round(data.standard_deviation / TEMPERATURE_RESOLUTION)
        min_raw = round(data.minimum / TEMPERATURE_RESOLUTION)
        max_raw = round(data.maximum / TEMPERATURE_RESOLUTION)
        dur_raw = _encode_time_exponential(data.sensing_duration)

        for name, value in [
            ("average", avg_raw),
            ("standard_deviation", std_raw),
            ("minimum", min_raw),
            ("maximum", max_raw),
        ]:
            if not SINT16_MIN <= value <= SINT16_MAX:
                raise ValueError(f"{name} raw {value} exceeds sint16 range")
        if not 0 <= dur_raw <= UINT8_MAX:
            raise ValueError(f"Duration raw {dur_raw} exceeds uint8 range")

        result = bytearray()
        result.extend(DataParser.encode_int16(avg_raw, signed=True))
        result.extend(DataParser.encode_int16(std_raw, signed=True))
        result.extend(DataParser.encode_int16(min_raw, signed=True))
        result.extend(DataParser.encode_int16(max_raw, signed=True))
        result.extend(DataParser.encode_int8(dur_raw, signed=False))
        return result
