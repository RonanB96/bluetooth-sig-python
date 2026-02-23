"""Supported Resistance Level Range characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import UINT8_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

# Resolution: M=1, d=1, b=0 -> 10 unitless per raw unit
_RESOLUTION = 10.0


class SupportedResistanceLevelRangeData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for supported resistance level range.

    All values are unitless with resolution of 10 per raw unit.
    """

    minimum: float  # Minimum resistance level (unitless)
    maximum: float  # Maximum resistance level (unitless)
    minimum_increment: float  # Minimum increment (unitless)

    def __post_init__(self) -> None:
        """Validate resistance level range data."""
        if self.minimum > self.maximum:
            raise ValueError(f"Minimum resistance level {self.minimum} cannot be greater than maximum {self.maximum}")
        max_value = UINT8_MAX * _RESOLUTION
        for name, val in [
            ("minimum", self.minimum),
            ("maximum", self.maximum),
            ("minimum_increment", self.minimum_increment),
        ]:
            if not 0.0 <= val <= max_value:
                raise ValueError(f"{name} {val} is outside valid range (0.0 to {max_value})")


class SupportedResistanceLevelRangeCharacteristic(
    BaseCharacteristic[SupportedResistanceLevelRangeData],
):
    """Supported Resistance Level Range characteristic (0x2AD6).

    org.bluetooth.characteristic.supported_resistance_level_range

    Represents the resistance level range supported by a fitness machine.
    Three fields: minimum resistance level, maximum resistance level,
    and minimum increment. Each is a uint8 with M=1, d=1, b=0 (resolution 10).
    """

    # Validation attributes
    expected_length: int = 3  # 3 x uint8
    min_length: int = 3

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> SupportedResistanceLevelRangeData:
        """Parse supported resistance level range data.

        Args:
            data: Raw bytes from the characteristic read.
            ctx: Optional CharacteristicContext (may be None).
            validate: Whether to validate ranges (default True).

        Returns:
            SupportedResistanceLevelRangeData with minimum, maximum, and
            increment values.

        """
        min_raw = DataParser.parse_int8(data, 0, signed=False)
        max_raw = DataParser.parse_int8(data, 1, signed=False)
        inc_raw = DataParser.parse_int8(data, 2, signed=False)

        return SupportedResistanceLevelRangeData(
            minimum=min_raw * _RESOLUTION,
            maximum=max_raw * _RESOLUTION,
            minimum_increment=inc_raw * _RESOLUTION,
        )

    def _encode_value(self, data: SupportedResistanceLevelRangeData) -> bytearray:
        """Encode supported resistance level range to bytes.

        Args:
            data: SupportedResistanceLevelRangeData instance.

        Returns:
            Encoded bytes (3 x uint8).

        """
        if not isinstance(data, SupportedResistanceLevelRangeData):
            raise TypeError(f"Expected SupportedResistanceLevelRangeData, got {type(data).__name__}")

        min_raw = round(data.minimum / _RESOLUTION)
        max_raw = round(data.maximum / _RESOLUTION)
        inc_raw = round(data.minimum_increment / _RESOLUTION)

        for name, value in [
            ("minimum", min_raw),
            ("maximum", max_raw),
            ("increment", inc_raw),
        ]:
            if not 0 <= value <= UINT8_MAX:
                raise ValueError(f"Resistance {name} raw value {value} exceeds uint8 range (0 to {UINT8_MAX})")

        result = bytearray()
        result.extend(DataParser.encode_int8(min_raw, signed=False))
        result.extend(DataParser.encode_int8(max_raw, signed=False))
        result.extend(DataParser.encode_int8(inc_raw, signed=False))
        return result
