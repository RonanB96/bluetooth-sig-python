"""Relative Value in an Illuminance Range characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import UINT8_MAX, UINT24_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_PERCENTAGE_RESOLUTION = 0.5  # Percentage 8: M=1, d=0, b=-1 -> 0.5%
_ILLUMINANCE_RESOLUTION = 0.01  # Illuminance: M=1, d=-2, b=0 -> 0.01 lux


class RelativeValueInAnIlluminanceRangeData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for relative value in an illuminance range.

    Combines a percentage (0.5% resolution) with an illuminance range
    (min/max in lux, 0.01 lux resolution).
    """

    relative_value: float  # Percentage (0.5% resolution)
    minimum_illuminance: float  # Minimum illuminance in lux
    maximum_illuminance: float  # Maximum illuminance in lux

    def __post_init__(self) -> None:
        """Validate data fields."""
        max_pct = UINT8_MAX * _PERCENTAGE_RESOLUTION
        if not 0.0 <= self.relative_value <= max_pct:
            raise ValueError(f"Relative value {self.relative_value}% is outside valid range (0.0 to {max_pct})")
        if self.minimum_illuminance > self.maximum_illuminance:
            raise ValueError(
                f"Minimum illuminance {self.minimum_illuminance} lux "
                f"cannot exceed maximum {self.maximum_illuminance} lux"
            )
        max_lux = UINT24_MAX * _ILLUMINANCE_RESOLUTION
        for name, val in [
            ("minimum_illuminance", self.minimum_illuminance),
            ("maximum_illuminance", self.maximum_illuminance),
        ]:
            if not 0.0 <= val <= max_lux:
                raise ValueError(f"{name} {val} lux is outside valid range (0.0 to {max_lux})")


class RelativeValueInAnIlluminanceRangeCharacteristic(
    BaseCharacteristic[RelativeValueInAnIlluminanceRangeData],
):
    """Relative Value in an Illuminance Range characteristic (0x2B0A).

    org.bluetooth.characteristic.relative_value_in_an_illuminance_range

    Represents a relative value within an illuminance range. Fields:
    Percentage 8 (uint8, 0.5%), min illuminance (uint24, 0.01 lux),
    max illuminance (uint24, 0.01 lux).
    """

    expected_length: int = 7  # uint8 + 2 x uint24
    min_length: int = 7
    expected_type = RelativeValueInAnIlluminanceRangeData

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> RelativeValueInAnIlluminanceRangeData:
        """Parse relative value in an illuminance range.

        Args:
            data: Raw bytes (7 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            RelativeValueInAnIlluminanceRangeData.

        """
        pct_raw = DataParser.parse_int8(data, 0, signed=False)
        min_raw = DataParser.parse_int24(data, 1, signed=False)
        max_raw = DataParser.parse_int24(data, 4, signed=False)

        return RelativeValueInAnIlluminanceRangeData(
            relative_value=pct_raw * _PERCENTAGE_RESOLUTION,
            minimum_illuminance=min_raw * _ILLUMINANCE_RESOLUTION,
            maximum_illuminance=max_raw * _ILLUMINANCE_RESOLUTION,
        )

    def _encode_value(self, data: RelativeValueInAnIlluminanceRangeData) -> bytearray:
        """Encode relative value in an illuminance range.

        Args:
            data: RelativeValueInAnIlluminanceRangeData instance.

        Returns:
            Encoded bytes (7 bytes).

        """
        pct_raw = round(data.relative_value / _PERCENTAGE_RESOLUTION)
        min_raw = round(data.minimum_illuminance / _ILLUMINANCE_RESOLUTION)
        max_raw = round(data.maximum_illuminance / _ILLUMINANCE_RESOLUTION)

        if not 0 <= pct_raw <= UINT8_MAX:
            raise ValueError(f"Percentage raw {pct_raw} exceeds uint8 range")
        if not 0 <= min_raw <= UINT24_MAX:
            raise ValueError(f"Min illuminance raw {min_raw} exceeds uint24 range")
        if not 0 <= max_raw <= UINT24_MAX:
            raise ValueError(f"Max illuminance raw {max_raw} exceeds uint24 range")

        result = bytearray()
        result.extend(DataParser.encode_int8(pct_raw, signed=False))
        result.extend(DataParser.encode_int24(min_raw, signed=False))
        result.extend(DataParser.encode_int24(max_raw, signed=False))
        return result
