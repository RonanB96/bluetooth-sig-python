"""Electric Current Statistics characteristic implementation."""

from __future__ import annotations

import math

import msgspec

from ..constants import UINT8_MAX, UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_CURRENT_RESOLUTION = 0.01  # 0.01 A per raw unit
_MAX_CURRENT = UINT16_MAX * _CURRENT_RESOLUTION  # 655.35 A
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


class ElectricCurrentStatisticsData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for electric current statistics.

    Five fields per GSS YAML: Average (uint16, 0.01 A), Standard Deviation
    (uint16, 0.01 A), Minimum (uint16, 0.01 A), Maximum (uint16, 0.01 A),
    and Sensing Duration (uint8, Time Exponential 8).
    """

    average: float  # Average current in Amperes
    standard_deviation: float  # Standard deviation in Amperes
    minimum: float  # Minimum current in Amperes
    maximum: float  # Maximum current in Amperes
    sensing_duration: float  # Sensing duration in seconds (exponential encoding)

    def __post_init__(self) -> None:
        """Validate current statistics data."""
        if self.minimum > self.maximum:
            raise ValueError(f"Minimum current {self.minimum} A cannot be greater than maximum {self.maximum} A")

        for name, current in [
            ("average", self.average),
            ("standard_deviation", self.standard_deviation),
            ("minimum", self.minimum),
            ("maximum", self.maximum),
        ]:
            if not 0.0 <= current <= _MAX_CURRENT:
                raise ValueError(
                    f"{name.capitalize()} current {current} A is outside valid range (0.0 to {_MAX_CURRENT} A)"
                )
        if self.sensing_duration < 0.0:
            raise ValueError(f"Sensing duration {self.sensing_duration} s cannot be negative")


class ElectricCurrentStatisticsCharacteristic(BaseCharacteristic[ElectricCurrentStatisticsData]):
    """Electric Current Statistics characteristic (0x2AF1).

    org.bluetooth.characteristic.electric_current_statistics

    Statistics for current measurements: average, standard deviation,
    minimum, maximum (all uint16, 0.01 A), and sensing duration
    (Time Exponential 8).
    """

    expected_length: int = 9  # 4x uint16 + uint8
    min_length: int = 9

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ElectricCurrentStatisticsData:
        """Parse current statistics data (4x uint16 + uint8)."""
        avg_raw = DataParser.parse_int16(data, 0, signed=False)
        std_raw = DataParser.parse_int16(data, 2, signed=False)
        min_raw = DataParser.parse_int16(data, 4, signed=False)
        max_raw = DataParser.parse_int16(data, 6, signed=False)
        dur_raw = DataParser.parse_int8(data, 8, signed=False)

        return ElectricCurrentStatisticsData(
            average=avg_raw * _CURRENT_RESOLUTION,
            standard_deviation=std_raw * _CURRENT_RESOLUTION,
            minimum=min_raw * _CURRENT_RESOLUTION,
            maximum=max_raw * _CURRENT_RESOLUTION,
            sensing_duration=_decode_time_exponential(dur_raw),
        )

    def _encode_value(self, data: ElectricCurrentStatisticsData) -> bytearray:
        """Encode electric current statistics value back to bytes."""
        avg_raw = round(data.average * 100)
        std_raw = round(data.standard_deviation * 100)
        min_raw = round(data.minimum * 100)
        max_raw = round(data.maximum * 100)
        dur_raw = _encode_time_exponential(data.sensing_duration)

        for name, value in [
            ("average", avg_raw),
            ("standard_deviation", std_raw),
            ("minimum", min_raw),
            ("maximum", max_raw),
        ]:
            if not 0 <= value <= UINT16_MAX:
                raise ValueError(f"Current {name} value {value} exceeds uint16 range")
        if not 0 <= dur_raw <= UINT8_MAX:
            raise ValueError(f"Duration raw {dur_raw} exceeds uint8 range")

        result = bytearray()
        result.extend(DataParser.encode_int16(avg_raw, signed=False))
        result.extend(DataParser.encode_int16(std_raw, signed=False))
        result.extend(DataParser.encode_int16(min_raw, signed=False))
        result.extend(DataParser.encode_int16(max_raw, signed=False))
        result.extend(DataParser.encode_int8(dur_raw, signed=False))

        return result
