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

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "int"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> int:
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
        feature_mask = struct.unpack("<I", data[:4])[0]
        return feature_mask

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""  # Feature bitmask has no unit

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return ""

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return ""