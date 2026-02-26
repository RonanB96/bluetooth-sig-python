"""Relative Runtime in a Correlated Color Temperature Range characteristic."""

from __future__ import annotations

import msgspec

from ..constants import UINT8_MAX, UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_PERCENTAGE_RESOLUTION = 0.5  # Percentage 8: M=1, d=0, b=-1 -> 0.5%
# Correlated Color Temperature: 1 Kelvin per raw unit (no scaling)


class RelativeRuntimeInACCTRangeData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for relative runtime in a correlated color temperature range.

    Combines a percentage (0.5% resolution) with a CCT range
    (min/max in Kelvin, 1 K resolution).
    """

    relative_runtime: float  # Percentage (0.5% resolution)
    minimum_cct: int  # Minimum correlated color temperature in K
    maximum_cct: int  # Maximum correlated color temperature in K

    def __post_init__(self) -> None:
        """Validate data fields."""
        max_pct = UINT8_MAX * _PERCENTAGE_RESOLUTION
        if not 0.0 <= self.relative_runtime <= max_pct:
            raise ValueError(f"Relative runtime {self.relative_runtime}% is outside valid range (0.0 to {max_pct})")
        if self.minimum_cct > self.maximum_cct:
            raise ValueError(f"Minimum CCT {self.minimum_cct} K cannot exceed maximum {self.maximum_cct} K")
        for name, val in [
            ("minimum_cct", self.minimum_cct),
            ("maximum_cct", self.maximum_cct),
        ]:
            if not 0 <= val <= UINT16_MAX:
                raise ValueError(f"{name} {val} K is outside valid range (0 to {UINT16_MAX})")


class RelativeRuntimeInACorrelatedColorTemperatureRangeCharacteristic(
    BaseCharacteristic[RelativeRuntimeInACCTRangeData],
):
    """Relative Runtime in a Correlated Color Temperature Range (0x2BE5).

    org.bluetooth.characteristic.relative_runtime_in_a_correlated_color_temperature_range

    Represents relative runtime within a CCT range. Fields:
    Percentage 8 (uint8, 0.5%), min CCT (uint16, 1 K),
    max CCT (uint16, 1 K).
    """

    expected_length: int = 5  # uint8 + 2 x uint16
    min_length: int = 5

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> RelativeRuntimeInACCTRangeData:
        """Parse relative runtime in a CCT range.

        Args:
            data: Raw bytes (5 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            RelativeRuntimeInACCTRangeData.

        """
        pct_raw = DataParser.parse_int8(data, 0, signed=False)
        min_raw = DataParser.parse_int16(data, 1, signed=False)
        max_raw = DataParser.parse_int16(data, 3, signed=False)

        return RelativeRuntimeInACCTRangeData(
            relative_runtime=pct_raw * _PERCENTAGE_RESOLUTION,
            minimum_cct=min_raw,
            maximum_cct=max_raw,
        )

    def _encode_value(self, data: RelativeRuntimeInACCTRangeData) -> bytearray:
        """Encode relative runtime in a CCT range.

        Args:
            data: RelativeRuntimeInACCTRangeData instance.

        Returns:
            Encoded bytes (5 bytes).

        """
        pct_raw = round(data.relative_runtime / _PERCENTAGE_RESOLUTION)

        if not 0 <= pct_raw <= UINT8_MAX:
            raise ValueError(f"Percentage raw {pct_raw} exceeds uint8 range")
        if not 0 <= data.minimum_cct <= UINT16_MAX:
            raise ValueError(f"Min CCT {data.minimum_cct} exceeds uint16 range")
        if not 0 <= data.maximum_cct <= UINT16_MAX:
            raise ValueError(f"Max CCT {data.maximum_cct} exceeds uint16 range")

        result = bytearray()
        result.extend(DataParser.encode_int8(pct_raw, signed=False))
        result.extend(DataParser.encode_int16(data.minimum_cct, signed=False))
        result.extend(DataParser.encode_int16(data.maximum_cct, signed=False))
        return result
