"""Voltage Statistics characteristic implementation."""

from __future__ import annotations

import math

import msgspec

from ..constants import UINT8_MAX, UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_VOLTAGE_RESOLUTION = 1 / 64.0  # 1/64 V per raw unit
_MAX_VOLTAGE = UINT16_MAX * _VOLTAGE_RESOLUTION  # ~1023.98 V
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


class VoltageStatisticsData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for voltage statistics.

    Five fields per spec: Average (uint16, 1/64 V), Standard Deviation
    (uint16, 1/64 V), Minimum (uint16, 1/64 V), Maximum (uint16, 1/64 V),
    and Sensing Duration (uint8, Time Exponential 8).
    """

    average: float  # Average voltage in Volts
    standard_deviation: float  # Standard deviation in Volts
    minimum: float  # Minimum voltage in Volts
    maximum: float  # Maximum voltage in Volts
    sensing_duration: float  # Sensing duration in seconds (exponential encoding)

    def __post_init__(self) -> None:
        """Validate voltage statistics data."""
        if self.minimum > self.maximum:
            raise ValueError(f"Minimum voltage {self.minimum} V cannot be greater than maximum {self.maximum} V")

        for name, voltage in [
            ("average", self.average),
            ("standard_deviation", self.standard_deviation),
            ("minimum", self.minimum),
            ("maximum", self.maximum),
        ]:
            if not 0.0 <= voltage <= _MAX_VOLTAGE:
                raise ValueError(
                    f"{name.capitalize()} voltage {voltage} V is outside valid range (0.0 to {_MAX_VOLTAGE:.2f} V)"
                )
        if self.sensing_duration < 0.0:
            raise ValueError(f"Sensing duration {self.sensing_duration} s cannot be negative")


class VoltageStatisticsCharacteristic(BaseCharacteristic[VoltageStatisticsData]):
    """Voltage Statistics characteristic (0x2B1A).

    org.bluetooth.characteristic.voltage_statistics

    Statistics for Voltage measurements: average, standard deviation,
    minimum, maximum (all uint16, 1/64 V), and sensing duration
    (Time Exponential 8).
    """

    expected_length: int = 9  # 4x uint16 + uint8
    min_length: int = 9

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> VoltageStatisticsData:
        """Parse voltage statistics data (4x uint16 + uint8)."""
        avg_raw = DataParser.parse_int16(data, 0, signed=False)
        std_raw = DataParser.parse_int16(data, 2, signed=False)
        min_raw = DataParser.parse_int16(data, 4, signed=False)
        max_raw = DataParser.parse_int16(data, 6, signed=False)
        dur_raw = DataParser.parse_int8(data, 8, signed=False)

        return VoltageStatisticsData(
            average=avg_raw / 64.0,
            standard_deviation=std_raw / 64.0,
            minimum=min_raw / 64.0,
            maximum=max_raw / 64.0,
            sensing_duration=_decode_time_exponential(dur_raw),
        )

    def _encode_value(self, data: VoltageStatisticsData) -> bytearray:
        """Encode voltage statistics value back to bytes."""
        if not isinstance(data, VoltageStatisticsData):
            raise TypeError(f"Voltage statistics data must be a VoltageStatisticsData, got {type(data).__name__}")

        avg_raw = round(data.average * 64)
        std_raw = round(data.standard_deviation * 64)
        min_raw = round(data.minimum * 64)
        max_raw = round(data.maximum * 64)
        dur_raw = _encode_time_exponential(data.sensing_duration)

        # pylint: disable=duplicate-code
        for name, value in [
            ("average", avg_raw),
            ("standard_deviation", std_raw),
            ("minimum", min_raw),
            ("maximum", max_raw),
        ]:
            if not 0 <= value <= UINT16_MAX:
                raise ValueError(f"Voltage {name} value {value} exceeds uint16 range")
        if not 0 <= dur_raw <= UINT8_MAX:
            raise ValueError(f"Duration raw {dur_raw} exceeds uint8 range")

        result = bytearray()
        result.extend(DataParser.encode_int16(avg_raw, signed=False))
        result.extend(DataParser.encode_int16(std_raw, signed=False))
        result.extend(DataParser.encode_int16(min_raw, signed=False))
        result.extend(DataParser.encode_int16(max_raw, signed=False))
        result.extend(DataParser.encode_int8(dur_raw, signed=False))

        return result
