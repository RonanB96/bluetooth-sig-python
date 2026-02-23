"""Supported Speed Range characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

# Resolution: M=1, d=-2, b=0 → 0.01 km/h
_RESOLUTION = 0.01


class SupportedSpeedRangeData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for supported speed range.

    All values are in kilometres per hour with 0.01 km/h resolution.
    """

    minimum: float  # Minimum speed in km/h
    maximum: float  # Maximum speed in km/h
    minimum_increment: float  # Minimum increment in km/h

    def __post_init__(self) -> None:
        """Validate speed range data."""
        if self.minimum > self.maximum:
            raise ValueError(f"Minimum speed {self.minimum} km/h cannot be greater than maximum {self.maximum} km/h")
        max_value = UINT16_MAX * _RESOLUTION
        for name, val in [
            ("minimum", self.minimum),
            ("maximum", self.maximum),
            ("minimum_increment", self.minimum_increment),
        ]:
            if not 0.0 <= val <= max_value:
                raise ValueError(f"{name} {val} km/h is outside valid range (0.0 to {max_value})")


class SupportedSpeedRangeCharacteristic(BaseCharacteristic[SupportedSpeedRangeData]):
    """Supported Speed Range characteristic (0x2AD4).

    org.bluetooth.characteristic.supported_speed_range

    Represents the speed range supported by a fitness machine.
    Three fields: minimum speed, maximum speed, and minimum increment.
    Each is a uint16 with M=1, d=-2, b=0 (0.01 km/h resolution).
    """

    # Validation attributes
    expected_length: int = 6  # 3 x uint16
    min_length: int = 6

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> SupportedSpeedRangeData:
        """Parse supported speed range data (3 x uint16, 0.01 km/h resolution).

        Args:
            data: Raw bytes from the characteristic read.
            ctx: Optional CharacteristicContext (may be None).
            validate: Whether to validate ranges (default True).

        Returns:
            SupportedSpeedRangeData with minimum, maximum, and increment values.

        """
        min_raw = DataParser.parse_int16(data, 0, signed=False)
        max_raw = DataParser.parse_int16(data, 2, signed=False)
        inc_raw = DataParser.parse_int16(data, 4, signed=False)

        return SupportedSpeedRangeData(
            minimum=min_raw * _RESOLUTION,
            maximum=max_raw * _RESOLUTION,
            minimum_increment=inc_raw * _RESOLUTION,
        )

    def _encode_value(self, data: SupportedSpeedRangeData) -> bytearray:
        """Encode supported speed range to bytes.

        Args:
            data: SupportedSpeedRangeData instance.

        Returns:
            Encoded bytes (3 x uint16, little-endian).

        """
        if not isinstance(data, SupportedSpeedRangeData):
            raise TypeError(f"Expected SupportedSpeedRangeData, got {type(data).__name__}")

        min_raw = round(data.minimum / _RESOLUTION)
        max_raw = round(data.maximum / _RESOLUTION)
        inc_raw = round(data.minimum_increment / _RESOLUTION)

        for name, value in [("minimum", min_raw), ("maximum", max_raw), ("increment", inc_raw)]:
            if not 0 <= value <= UINT16_MAX:
                raise ValueError(f"Speed {name} raw value {value} exceeds uint16 range")

        result = bytearray()
        result.extend(DataParser.encode_int16(min_raw, signed=False))
        result.extend(DataParser.encode_int16(max_raw, signed=False))
        result.extend(DataParser.encode_int16(inc_raw, signed=False))
        return result
