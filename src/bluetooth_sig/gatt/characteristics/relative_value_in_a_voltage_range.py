"""Relative Value in a Voltage Range characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import UINT8_MAX, UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_PERCENTAGE_RESOLUTION = 0.5  # Percentage 8: M=1, d=0, b=-1 -> 0.5%
_VOLTAGE_RESOLUTION = 1 / 64  # Voltage: M=1, d=0, b=-6 -> 1/64 V


class RelativeValueInAVoltageRangeData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for relative value in a voltage range.

    Combines a percentage (0.5% resolution) with a voltage range
    (min/max in volts, 1/64 V resolution).
    """

    relative_value: float  # Percentage (0.5% resolution)
    minimum_voltage: float  # Minimum voltage in V
    maximum_voltage: float  # Maximum voltage in V

    def __post_init__(self) -> None:
        """Validate data fields."""
        max_pct = UINT8_MAX * _PERCENTAGE_RESOLUTION
        if not 0.0 <= self.relative_value <= max_pct:
            raise ValueError(f"Relative value {self.relative_value}% is outside valid range (0.0 to {max_pct})")
        if self.minimum_voltage > self.maximum_voltage:
            raise ValueError(f"Minimum voltage {self.minimum_voltage} V cannot exceed maximum {self.maximum_voltage} V")
        max_voltage = UINT16_MAX * _VOLTAGE_RESOLUTION
        for name, val in [
            ("minimum_voltage", self.minimum_voltage),
            ("maximum_voltage", self.maximum_voltage),
        ]:
            if not 0.0 <= val <= max_voltage:
                raise ValueError(f"{name} {val} V is outside valid range (0.0 to {max_voltage})")


class RelativeValueInAVoltageRangeCharacteristic(
    BaseCharacteristic[RelativeValueInAVoltageRangeData],
):
    """Relative Value in a Voltage Range characteristic (0x2B09).

    org.bluetooth.characteristic.relative_value_in_a_voltage_range

    Represents a relative value within a voltage range. Fields:
    Percentage 8 (uint8, 0.5%), min voltage (uint16, 1/64 V),
    max voltage (uint16, 1/64 V).
    """

    expected_length: int = 5  # uint8 + 2 x uint16
    min_length: int = 5
    expected_type = RelativeValueInAVoltageRangeData

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> RelativeValueInAVoltageRangeData:
        """Parse relative value in a voltage range.

        Args:
            data: Raw bytes (5 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            RelativeValueInAVoltageRangeData.

        """
        pct_raw = DataParser.parse_int8(data, 0, signed=False)
        min_raw = DataParser.parse_int16(data, 1, signed=False)
        max_raw = DataParser.parse_int16(data, 3, signed=False)

        return RelativeValueInAVoltageRangeData(
            relative_value=pct_raw * _PERCENTAGE_RESOLUTION,
            minimum_voltage=min_raw * _VOLTAGE_RESOLUTION,
            maximum_voltage=max_raw * _VOLTAGE_RESOLUTION,
        )

    def _encode_value(self, data: RelativeValueInAVoltageRangeData) -> bytearray:
        """Encode relative value in a voltage range.

        Args:
            data: RelativeValueInAVoltageRangeData instance.

        Returns:
            Encoded bytes (5 bytes).

        """
        pct_raw = round(data.relative_value / _PERCENTAGE_RESOLUTION)
        min_raw = round(data.minimum_voltage / _VOLTAGE_RESOLUTION)
        max_raw = round(data.maximum_voltage / _VOLTAGE_RESOLUTION)

        if not 0 <= pct_raw <= UINT8_MAX:
            raise ValueError(f"Percentage raw {pct_raw} exceeds uint8 range")
        if not 0 <= min_raw <= UINT16_MAX:
            raise ValueError(f"Min voltage raw {min_raw} exceeds uint16 range")
        if not 0 <= max_raw <= UINT16_MAX:
            raise ValueError(f"Max voltage raw {max_raw} exceeds uint16 range")

        result = bytearray()
        result.extend(DataParser.encode_int8(pct_raw, signed=False))
        result.extend(DataParser.encode_int16(min_raw, signed=False))
        result.extend(DataParser.encode_int16(max_raw, signed=False))
        return result
