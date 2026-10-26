"""Relative Runtime in a Generic Level Range characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import UINT8_MAX, UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_PERCENTAGE_RESOLUTION = 0.5  # Percentage 8: M=1, d=0, b=-1 -> 0.5%
# Generic Level: M=1, d=0, b=0 -> unitless, no scaling


class RelativeRuntimeInAGenericLevelRangeData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for relative runtime in a generic level range.

    Combines a percentage (0.5% resolution) with a generic level range
    (min/max as raw uint16 values, unitless).
    """

    relative_value: float  # Percentage (0.5% resolution)
    minimum_generic_level: int  # Minimum generic level (unitless)
    maximum_generic_level: int  # Maximum generic level (unitless)

    def __post_init__(self) -> None:
        """Validate data fields."""
        max_pct = UINT8_MAX * _PERCENTAGE_RESOLUTION
        if not 0.0 <= self.relative_value <= max_pct:
            raise ValueError(f"Relative value {self.relative_value}% is outside valid range (0.0 to {max_pct})")
        if self.minimum_generic_level > self.maximum_generic_level:
            raise ValueError(
                f"Minimum generic level {self.minimum_generic_level} cannot exceed maximum {self.maximum_generic_level}"
            )
        for name, val in [
            ("minimum_generic_level", self.minimum_generic_level),
            ("maximum_generic_level", self.maximum_generic_level),
        ]:
            if not 0 <= val <= UINT16_MAX:
                raise ValueError(f"{name} {val} is outside valid range (0 to {UINT16_MAX})")


class RelativeRuntimeInAGenericLevelRangeCharacteristic(
    BaseCharacteristic[RelativeRuntimeInAGenericLevelRangeData],
):
    """Relative Runtime in a Generic Level Range characteristic (0x2B08).

    org.bluetooth.characteristic.relative_runtime_in_a_generic_level_range

    Represents relative runtime within a generic level range. Fields:
    Percentage 8 (uint8, 0.5%), min level (uint16, unitless),
    max level (uint16, unitless).
    """

    expected_length: int = 5  # uint8 + 2 x uint16
    min_length: int = 5

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> RelativeRuntimeInAGenericLevelRangeData:
        """Parse relative runtime in a generic level range.

        Args:
            data: Raw bytes (5 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            RelativeRuntimeInAGenericLevelRangeData.

        """
        pct_raw = DataParser.parse_int8(data, 0, signed=False)
        min_raw = DataParser.parse_int16(data, 1, signed=False)
        max_raw = DataParser.parse_int16(data, 3, signed=False)

        return RelativeRuntimeInAGenericLevelRangeData(
            relative_value=pct_raw * _PERCENTAGE_RESOLUTION,
            minimum_generic_level=min_raw,
            maximum_generic_level=max_raw,
        )

    def _encode_value(self, data: RelativeRuntimeInAGenericLevelRangeData) -> bytearray:
        """Encode relative runtime in a generic level range.

        Args:
            data: RelativeRuntimeInAGenericLevelRangeData instance.

        Returns:
            Encoded bytes (5 bytes).

        """
        pct_raw = round(data.relative_value / _PERCENTAGE_RESOLUTION)

        if not 0 <= pct_raw <= UINT8_MAX:
            raise ValueError(f"Percentage raw {pct_raw} exceeds uint8 range")
        if not 0 <= data.minimum_generic_level <= UINT16_MAX:
            raise ValueError(f"Min level {data.minimum_generic_level} exceeds uint16 range")
        if not 0 <= data.maximum_generic_level <= UINT16_MAX:
            raise ValueError(f"Max level {data.maximum_generic_level} exceeds uint16 range")

        result = bytearray()
        result.extend(DataParser.encode_int8(pct_raw, signed=False))
        result.extend(DataParser.encode_int16(data.minimum_generic_level, signed=False))
        result.extend(DataParser.encode_int16(data.maximum_generic_level, signed=False))
        return result
