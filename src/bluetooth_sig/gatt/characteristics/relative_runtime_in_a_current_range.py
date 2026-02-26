"""Relative Runtime in a Current Range characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import UINT8_MAX, UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_PERCENTAGE_RESOLUTION = 0.5  # Percentage 8: M=1, d=0, b=-1 -> 0.5%
_CURRENT_RESOLUTION = 0.01  # Electric Current: M=1, d=-2, b=0 -> 0.01 A


class RelativeRuntimeInACurrentRangeData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for relative runtime in a current range.

    Combines a percentage (0.5% resolution) with a current range
    (min/max in amperes, 0.01 A resolution).
    """

    relative_runtime: float  # Percentage (0.5% resolution)
    minimum_current: float  # Minimum current in A
    maximum_current: float  # Maximum current in A

    def __post_init__(self) -> None:
        """Validate data fields."""
        max_pct = UINT8_MAX * _PERCENTAGE_RESOLUTION
        if not 0.0 <= self.relative_runtime <= max_pct:
            raise ValueError(f"Relative runtime {self.relative_runtime}% is outside valid range (0.0 to {max_pct})")
        if self.minimum_current > self.maximum_current:
            raise ValueError(f"Minimum current {self.minimum_current} A cannot exceed maximum {self.maximum_current} A")
        max_current = UINT16_MAX * _CURRENT_RESOLUTION
        for name, val in [
            ("minimum_current", self.minimum_current),
            ("maximum_current", self.maximum_current),
        ]:
            if not 0.0 <= val <= max_current:
                raise ValueError(f"{name} {val} A is outside valid range (0.0 to {max_current})")


class RelativeRuntimeInACurrentRangeCharacteristic(
    BaseCharacteristic[RelativeRuntimeInACurrentRangeData],
):
    """Relative Runtime in a Current Range characteristic (0x2B07).

    org.bluetooth.characteristic.relative_runtime_in_a_current_range

    Represents relative runtime within an electric current range. Fields:
    Percentage 8 (uint8, 0.5%), min current (uint16, 0.01 A),
    max current (uint16, 0.01 A).
    """

    expected_length: int = 5  # uint8 + 2 x uint16
    min_length: int = 5

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> RelativeRuntimeInACurrentRangeData:
        """Parse relative runtime in a current range.

        Args:
            data: Raw bytes (5 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            RelativeRuntimeInACurrentRangeData.

        """
        pct_raw = DataParser.parse_int8(data, 0, signed=False)
        min_raw = DataParser.parse_int16(data, 1, signed=False)
        max_raw = DataParser.parse_int16(data, 3, signed=False)

        return RelativeRuntimeInACurrentRangeData(
            relative_runtime=pct_raw * _PERCENTAGE_RESOLUTION,
            minimum_current=min_raw * _CURRENT_RESOLUTION,
            maximum_current=max_raw * _CURRENT_RESOLUTION,
        )

    def _encode_value(self, data: RelativeRuntimeInACurrentRangeData) -> bytearray:
        """Encode relative runtime in a current range.

        Args:
            data: RelativeRuntimeInACurrentRangeData instance.

        Returns:
            Encoded bytes (5 bytes).

        """
        pct_raw = round(data.relative_runtime / _PERCENTAGE_RESOLUTION)
        min_raw = round(data.minimum_current / _CURRENT_RESOLUTION)
        max_raw = round(data.maximum_current / _CURRENT_RESOLUTION)

        if not 0 <= pct_raw <= UINT8_MAX:
            raise ValueError(f"Percentage raw {pct_raw} exceeds uint8 range")
        if not 0 <= min_raw <= UINT16_MAX:
            raise ValueError(f"Min current raw {min_raw} exceeds uint16 range")
        if not 0 <= max_raw <= UINT16_MAX:
            raise ValueError(f"Max current raw {max_raw} exceeds uint16 range")

        result = bytearray()
        result.extend(DataParser.encode_int8(pct_raw, signed=False))
        result.extend(DataParser.encode_int16(min_raw, signed=False))
        result.extend(DataParser.encode_int16(max_raw, signed=False))
        return result
