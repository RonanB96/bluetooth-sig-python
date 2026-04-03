"""Average Current characteristic implementation."""

from __future__ import annotations

import math

import msgspec

from ...types.units import ElectricalUnit
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_CURRENT_RESOLUTION = 0.01  # 0.01 A per raw unit (uint16)
_TIME_EXP_BASE = 1.1
_TIME_EXP_OFFSET = 64


def _decode_time_exponential(raw: int) -> float:
    """Decode Time Exponential 8 raw uint8 to seconds."""
    if raw == 0:
        return 0.0
    return _TIME_EXP_BASE ** (raw - _TIME_EXP_OFFSET)


def _encode_time_exponential(seconds: float) -> int:
    """Encode seconds to Time Exponential 8 raw uint8."""
    if seconds <= 0.0:
        return 0
    n = round(math.log(seconds) / math.log(_TIME_EXP_BASE) + _TIME_EXP_OFFSET)
    return max(1, min(n, 0xFD))


class AverageCurrentData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Average Current characteristic."""

    current: float  # Electric current in Amperes
    sensing_duration: float  # Sensing duration in seconds (Time Exponential 8)


class AverageCurrentCharacteristic(BaseCharacteristic[AverageCurrentData]):
    """Average Current characteristic (0x2AE0).

    org.bluetooth.characteristic.average_current

    Average electric current over a sensing duration.

    Format per GSS YAML: Electric Current Value (uint16, 0.01 A/unit) +
    Sensing Duration (uint8, Time Exponential 8).
    """

    _manual_unit: str = ElectricalUnit.AMPS.value
    expected_length: int = 3
    min_length: int = 3

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> AverageCurrentData:
        """Parse average current data per Bluetooth SIG GSS spec.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext (may be None).
            validate: Whether to validate ranges (default True).

        Returns:
            AverageCurrentData with current in Amperes and sensing_duration in seconds.

        """
        raw_current = DataParser.parse_int16(data, 0, signed=False)
        raw_duration = DataParser.parse_int8(data, 2, signed=False)
        return AverageCurrentData(
            current=raw_current * _CURRENT_RESOLUTION,
            sensing_duration=_decode_time_exponential(raw_duration),
        )

    def _encode_value(self, data: AverageCurrentData) -> bytearray:
        """Encode AverageCurrentData to bytes.

        Args:
            data: AverageCurrentData instance to encode.

        Returns:
            Encoded 3-byte bytearray.

        """
        raw_current = round(data.current / _CURRENT_RESOLUTION)
        result = DataParser.encode_int16(raw_current, signed=False)
        result += DataParser.encode_int8(_encode_time_exponential(data.sensing_duration))
        return result
