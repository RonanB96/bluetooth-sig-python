"""Relative Value in a Temperature Range characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import SINT16_MAX, SINT16_MIN, UINT8_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_PERCENTAGE_RESOLUTION = 0.5  # Percentage 8: M=1, d=0, b=-1 -> 0.5%
_TEMPERATURE_RESOLUTION = 0.01  # Temperature: M=1, d=-2, b=0 -> 0.01 C


class RelativeValueInATemperatureRangeData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for relative value in a temperature range.

    Combines a percentage (0.5% resolution) with a temperature range
    (min/max in degrees Celsius, 0.01 C resolution).
    """

    relative_value: float  # Percentage (0.5% resolution)
    minimum_temperature: float  # Minimum temperature in C
    maximum_temperature: float  # Maximum temperature in C

    def __post_init__(self) -> None:
        """Validate data fields."""
        max_pct = UINT8_MAX * _PERCENTAGE_RESOLUTION
        if not 0.0 <= self.relative_value <= max_pct:
            raise ValueError(f"Relative value {self.relative_value}% is outside valid range (0.0 to {max_pct})")
        if self.minimum_temperature > self.maximum_temperature:
            raise ValueError(
                f"Minimum temperature {self.minimum_temperature} C cannot exceed maximum {self.maximum_temperature} C"
            )


class RelativeValueInATemperatureRangeCharacteristic(
    BaseCharacteristic[RelativeValueInATemperatureRangeData],
):
    """Relative Value in a Temperature Range characteristic (0x2B0C).

    org.bluetooth.characteristic.relative_value_in_a_temperature_range

    Represents a relative value within a temperature range. Fields:
    Percentage 8 (uint8, 0.5%), min temperature (sint16, 0.01 C),
    max temperature (sint16, 0.01 C).
    """

    expected_length: int = 5  # uint8 + 2 x sint16
    min_length: int = 5
    expected_type = RelativeValueInATemperatureRangeData

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> RelativeValueInATemperatureRangeData:
        """Parse relative value in a temperature range.

        Args:
            data: Raw bytes (5 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            RelativeValueInATemperatureRangeData.

        """
        pct_raw = DataParser.parse_int8(data, 0, signed=False)
        min_raw = DataParser.parse_int16(data, 1, signed=True)
        max_raw = DataParser.parse_int16(data, 3, signed=True)

        return RelativeValueInATemperatureRangeData(
            relative_value=pct_raw * _PERCENTAGE_RESOLUTION,
            minimum_temperature=min_raw * _TEMPERATURE_RESOLUTION,
            maximum_temperature=max_raw * _TEMPERATURE_RESOLUTION,
        )

    def _encode_value(self, data: RelativeValueInATemperatureRangeData) -> bytearray:
        """Encode relative value in a temperature range.

        Args:
            data: RelativeValueInATemperatureRangeData instance.

        Returns:
            Encoded bytes (5 bytes).

        """
        pct_raw = round(data.relative_value / _PERCENTAGE_RESOLUTION)
        min_raw = round(data.minimum_temperature / _TEMPERATURE_RESOLUTION)
        max_raw = round(data.maximum_temperature / _TEMPERATURE_RESOLUTION)

        if not 0 <= pct_raw <= UINT8_MAX:
            raise ValueError(f"Percentage raw {pct_raw} exceeds uint8 range")
        if not SINT16_MIN <= min_raw <= SINT16_MAX:
            raise ValueError(f"Min temperature raw {min_raw} exceeds sint16 range")
        if not SINT16_MIN <= max_raw <= SINT16_MAX:
            raise ValueError(f"Max temperature raw {max_raw} exceeds sint16 range")

        result = bytearray()
        result.extend(DataParser.encode_int8(pct_raw, signed=False))
        result.extend(DataParser.encode_int16(min_raw, signed=True))
        result.extend(DataParser.encode_int16(max_raw, signed=True))
        return result
