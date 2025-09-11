"""Cycling Power Feature characteristic implementation."""

import struct
from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class CyclingPowerFeatureCharacteristic(BaseCharacteristic):
    """Cycling Power Feature characteristic (0x2A65).

    Used to expose the supported features of a cycling power sensor.
    Contains a 32-bit bitmask indicating supported measurement capabilities.
    """

    _characteristic_name: str = "Cycling Power Feature"

    def decode_value(self, data: bytearray) -> int:
        """Parse cycling power feature data.

        Format: 32-bit feature bitmask (little endian)

        Args:
            data: Raw bytearray from BLE characteristic

        Returns:
            32-bit feature bitmask as integer

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 4:
            raise ValueError("Cycling Power Feature data must be at least 4 bytes")

        # Parse 32-bit unsigned integer (little endian)
        feature_mask: int = struct.unpack("<I", data[:4])[0]
        return feature_mask

    def encode_value(self, data: int) -> bytearray:
        """Encode cycling power feature value back to bytes.

        Args:
            data: 32-bit feature bitmask as integer

        Returns:
            Encoded bytes representing the cycling power features (uint32)
        """
        feature_mask = int(data)

        # Validate range for uint32
        if not 0 <= feature_mask <= 0xFFFFFFFF:
            raise ValueError(f"Feature mask {feature_mask} exceeds uint32 range")

        return bytearray(struct.pack("<I", feature_mask))

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""  # Feature bitmask has no unit
