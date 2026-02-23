"""Chromaticity Coordinates characteristic implementation."""

from __future__ import annotations

import msgspec

from ..constants import UINT16_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

# Resolution: 1/65535 (same as Chromaticity Coordinate characteristic)
_RESOLUTION = 2**-16


class ChromaticityCoordinatesData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Data class for chromaticity coordinates.

    Each coordinate is a CIE 1931 chromaticity value in the range [0, 1).
    """

    x: float  # Chromaticity x-coordinate
    y: float  # Chromaticity y-coordinate

    def __post_init__(self) -> None:
        """Validate chromaticity coordinate data."""
        max_value = UINT16_MAX * _RESOLUTION
        for name, val in [("x", self.x), ("y", self.y)]:
            if not 0.0 <= val <= max_value:
                raise ValueError(f"Chromaticity {name}-coordinate {val} is outside valid range (0.0 to {max_value})")


class ChromaticityCoordinatesCharacteristic(BaseCharacteristic[ChromaticityCoordinatesData]):
    """Chromaticity Coordinates characteristic (0x2AE4).

    org.bluetooth.characteristic.chromaticity_coordinates

    Represents a pair of CIE 1931 chromaticity coordinates (x, y).
    Each coordinate is a uint16 with resolution 1/65535.
    """

    # Validation attributes
    expected_length: int = 4  # 2 x uint16
    min_length: int = 4

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ChromaticityCoordinatesData:
        """Parse chromaticity coordinates data (2 x uint16, resolution 1/65535).

        Args:
            data: Raw bytes from the characteristic read.
            ctx: Optional CharacteristicContext (may be None).
            validate: Whether to validate ranges (default True).

        Returns:
            ChromaticityCoordinatesData with x and y coordinate values.

        """
        x_raw = DataParser.parse_int16(data, 0, signed=False)
        y_raw = DataParser.parse_int16(data, 2, signed=False)

        return ChromaticityCoordinatesData(
            x=x_raw * _RESOLUTION,
            y=y_raw * _RESOLUTION,
        )

    def _encode_value(self, data: ChromaticityCoordinatesData) -> bytearray:
        """Encode chromaticity coordinates to bytes.

        Args:
            data: ChromaticityCoordinatesData instance.

        Returns:
            Encoded bytes (2 x uint16, little-endian).

        """
        if not isinstance(data, ChromaticityCoordinatesData):
            raise TypeError(f"Expected ChromaticityCoordinatesData, got {type(data).__name__}")

        x_raw = round(data.x / _RESOLUTION)
        y_raw = round(data.y / _RESOLUTION)

        for name, value in [("x", x_raw), ("y", y_raw)]:
            if not 0 <= value <= UINT16_MAX:
                raise ValueError(f"Chromaticity {name}-coordinate raw value {value} exceeds uint16 range")

        result = bytearray()
        result.extend(DataParser.encode_int16(x_raw, signed=False))
        result.extend(DataParser.encode_int16(y_raw, signed=False))
        return result
