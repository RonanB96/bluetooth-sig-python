"""Illuminance characteristic implementation."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils.data_parser import DataParser

# pylint: disable=duplicate-code
# Justification: This file follows the standard BLE characteristic base class pattern,
# which is intentionally duplicated across multiple characteristic implementations.
# These patterns are required by Bluetooth SIG specifications and represent legitimate
# code duplication for protocol compliance.


class IlluminanceCharacteristic(BaseCharacteristic[float]):
    """Illuminance characteristic (0x2AFB).

    Measures light intensity in lux (lumens per square meter).
    Uses uint24 (3 bytes) with 0.01 lux resolution.
    """

    resolution: float = 0.01

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float:
        """Decode illuminance characteristic.

        Decodes a 24-bit unsigned integer representing illuminance in 0.01 lux increments
        per Bluetooth SIG Illuminance characteristic specification.

        Args:
            data: Raw bytes from BLE characteristic (exactly 3 bytes, little-endian)
            ctx: Optional context for parsing (device info, flags, etc.)

        Returns:
            Illuminance in lux

        Raises:
            InsufficientDataError: If data is not exactly 3 bytes
        """
        raw_value = DataParser.parse_int24(data, 0, signed=False)
        return raw_value * self.resolution

    def _encode_value(self, data: float) -> bytearray:
        """Encode illuminance value."""
        raw_value = int(data / self.resolution)
        return DataParser.encode_int24(raw_value, signed=False)
