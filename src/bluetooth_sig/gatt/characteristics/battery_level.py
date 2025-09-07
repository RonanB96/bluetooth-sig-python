"""Battery level characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class BatteryLevelCharacteristic(BaseCharacteristic):
    """Battery level characteristic."""

    _characteristic_name: str = "Battery Level"

    def parse_value(self, data: bytearray) -> int:
        """Parse battery level data (uint8 in percentage)."""
        if not data:
            raise ValueError("Battery level data must be at least 1 byte")

        # Convert uint8 to percentage
        level = data[0]

        # Validate range
        if not 0 <= level <= 100:
            raise ValueError(f"Battery level must be 0-100, got {level}")

        return level

    def encode_value(self, data: int | float) -> bytearray:
        """Encode battery level back to bytes.

        Args:
            data: Battery level as integer (0-100)

        Returns:
            Encoded bytes representing the battery level
        """
        level = int(data)

        # Validate range
        if not 0 <= level <= 100:
            raise ValueError(f"Battery level must be 0-100, got {level}")

        return self._encode_uint8(level)
