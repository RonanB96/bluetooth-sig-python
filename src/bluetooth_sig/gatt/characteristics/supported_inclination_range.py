"""Supported Inclination Range characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import SINT16_MAX, SINT16_MIN, UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

# Resolution: M=1, d=-1, b=0 -> 0.1 percentage points
_RESOLUTION = 0.1


class SupportedInclinationRangeData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for supported inclination range.

    All values are in percentage with 0.1% resolution.
    Min/max may be negative (decline).
    """

    minimum: float  # Minimum inclination in %
    maximum: float  # Maximum inclination in %
    minimum_increment: float  # Minimum increment in %

    def __post_init__(self) -> None:
        """Validate inclination range data."""
        if self.minimum > self.maximum:
            raise ValueError(f"Minimum inclination {self.minimum}% cannot be greater than maximum {self.maximum}%")
        min_value = SINT16_MIN * _RESOLUTION
        max_value = SINT16_MAX * _RESOLUTION
        for name, val in [("minimum", self.minimum), ("maximum", self.maximum)]:
            if not min_value <= val <= max_value:
                raise ValueError(
                    f"{name.capitalize()} inclination {val}% is outside valid range ({min_value} to {max_value})"
                )
        inc_max = UINT16_MAX * _RESOLUTION
        if not 0.0 <= self.minimum_increment <= inc_max:
            raise ValueError(f"Minimum increment {self.minimum_increment}% is outside valid range (0.0 to {inc_max})")


class SupportedInclinationRangeCharacteristic(BaseCharacteristic[SupportedInclinationRangeData]):
    """Supported Inclination Range characteristic (0x2AD5).

    org.bluetooth.characteristic.supported_inclination_range

    Represents the inclination range supported by a fitness machine.
    Three fields: minimum inclination (sint16), maximum inclination (sint16),
    and minimum increment (uint16). All scaled M=1, d=-1, b=0 (0.1% resolution).
    """

    # Validation attributes
    expected_length: int = 6  # 2 x sint16 + 1 x uint16
    min_length: int = 6

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> SupportedInclinationRangeData:
        """Parse supported inclination range data.

        Args:
            data: Raw bytes from the characteristic read.
            ctx: Optional CharacteristicContext (may be None).
            validate: Whether to validate ranges (default True).

        Returns:
            SupportedInclinationRangeData with minimum, maximum, and increment.

        """
        min_raw = DataParser.parse_int16(data, 0, signed=True)
        max_raw = DataParser.parse_int16(data, 2, signed=True)
        inc_raw = DataParser.parse_int16(data, 4, signed=False)

        return SupportedInclinationRangeData(
            minimum=min_raw * _RESOLUTION,
            maximum=max_raw * _RESOLUTION,
            minimum_increment=inc_raw * _RESOLUTION,
        )

    def _encode_value(self, data: SupportedInclinationRangeData) -> bytearray:
        """Encode supported inclination range to bytes.

        Args:
            data: SupportedInclinationRangeData instance.

        Returns:
            Encoded bytes (2 x sint16 + 1 x uint16, little-endian).

        """
        if not isinstance(data, SupportedInclinationRangeData):
            raise TypeError(f"Expected SupportedInclinationRangeData, got {type(data).__name__}")

        min_raw = round(data.minimum / _RESOLUTION)
        max_raw = round(data.maximum / _RESOLUTION)
        inc_raw = round(data.minimum_increment / _RESOLUTION)

        for name, value, lo, hi in [
            ("minimum", min_raw, SINT16_MIN, SINT16_MAX),
            ("maximum", max_raw, SINT16_MIN, SINT16_MAX),
            ("increment", inc_raw, 0, UINT16_MAX),
        ]:
            if not lo <= value <= hi:
                raise ValueError(f"Inclination {name} raw value {value} exceeds range ({lo} to {hi})")

        result = bytearray()
        result.extend(DataParser.encode_int16(min_raw, signed=True))
        result.extend(DataParser.encode_int16(max_raw, signed=True))
        result.extend(DataParser.encode_int16(inc_raw, signed=False))
        return result
