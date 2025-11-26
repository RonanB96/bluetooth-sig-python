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


# Special value constants for Illuminance characteristic
class IlluminanceValues:  # pylint: disable=too-few-public-methods
    """Special values for Illuminance characteristic per Bluetooth SIG specification."""

    VALUE_UNKNOWN = 0xFFFFFF  # Indicates value is not known


class IlluminanceCharacteristic(BaseCharacteristic):
    """Illuminance characteristic (0x2AFB).

    Measures light intensity in lux (lumens per square meter).
    Uses uint24 (3 bytes) with 0.01 lux resolution.
    """

    resolution: float = 0.01

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float | None:
        """Decode illuminance characteristic.

        Decodes a 24-bit unsigned integer representing illuminance in 0.01 lux increments
        per Bluetooth SIG Illuminance characteristic specification.

        Args:
            data: Raw bytes from BLE characteristic (exactly 3 bytes, little-endian)
            ctx: Optional context for parsing (device info, flags, etc.)

        Returns:
            Illuminance in lux, or None if value is unknown (0xFFFFFF)

        Raises:
            InsufficientDataError: If data is not exactly 3 bytes
        """
        raw_value = DataParser.parse_int24(data, 0, signed=False)
        if raw_value == IlluminanceValues.VALUE_UNKNOWN:
            return None
        return raw_value * self.resolution

    def encode_value(self, data: float) -> bytearray:
        """Encode illuminance value."""
        raw_value = int(data / self.resolution)
        return DataParser.encode_int24(raw_value, signed=False)
