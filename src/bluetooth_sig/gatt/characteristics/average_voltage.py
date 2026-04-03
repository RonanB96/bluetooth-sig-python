"""Average Voltage characteristic implementation."""

from __future__ import annotations

import math

import msgspec

from ...types.units import ElectricalUnit
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_VOLTAGE_RESOLUTION = 1 / 64.0  # 1/64 V per raw unit (uint16)
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


class AverageVoltageData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Average Voltage characteristic."""

    voltage: float  # Voltage in Volts
    sensing_duration: float  # Sensing duration in seconds (Time Exponential 8)


class AverageVoltageCharacteristic(BaseCharacteristic[AverageVoltageData]):
    """Average Voltage characteristic (0x2AE1).

    org.bluetooth.characteristic.average_voltage

    Average voltage over a sensing duration.

    Format per GSS YAML: Voltage Value (uint16, 1/64 V/unit) +
    Sensing Duration (uint8, Time Exponential 8).
    """

    _manual_unit: str = ElectricalUnit.VOLTS.value
    expected_length: int = 3
    min_length: int = 3

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> AverageVoltageData:
        """Parse average voltage data per Bluetooth SIG GSS spec.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext (may be None).
            validate: Whether to validate ranges (default True).

        Returns:
            AverageVoltageData with voltage in Volts and sensing_duration in seconds.

        """
        raw_voltage = DataParser.parse_int16(data, 0, signed=False)
        raw_duration = DataParser.parse_int8(data, 2, signed=False)
        return AverageVoltageData(
            voltage=raw_voltage * _VOLTAGE_RESOLUTION,
            sensing_duration=_decode_time_exponential(raw_duration),
        )

    def _encode_value(self, data: AverageVoltageData) -> bytearray:
        """Encode AverageVoltageData to bytes.

        Args:
            data: AverageVoltageData instance to encode.

        Returns:
            Encoded 3-byte bytearray.

        """
        raw_voltage = round(data.voltage / _VOLTAGE_RESOLUTION)
        result = DataParser.encode_int16(raw_voltage, signed=False)
        result += DataParser.encode_int8(_encode_time_exponential(data.sensing_duration))
        return result
