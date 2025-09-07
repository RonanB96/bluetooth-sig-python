"""Battery level characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class BatteryLevelData:
    """Parsed data from Battery Level characteristic."""

    level: int
    unit: str = "%"

    def __post_init__(self):
        """Validate battery level data."""
        if not 0 <= self.level <= 100:
            raise ValueError(f"Battery level must be 0-100, got {self.level}")
        if self.unit != "%":
            raise ValueError(f"Battery level unit must be '%', got {self.unit}")

    def __eq__(self, other) -> bool:
        """Support comparison with integer values for backward compatibility."""
        if isinstance(other, int):
            return self.level == other
        return super().__eq__(other)

    def __int__(self) -> int:
        """Support integer conversion for backward compatibility."""
        return self.level

    def __str__(self) -> str:
        """String representation showing the level."""
        return str(self.level)


@dataclass
class BatteryLevelCharacteristic(BaseCharacteristic):
    """Battery level characteristic."""

    _characteristic_name: str = "Battery Level"

    def parse_value(self, data: bytearray) -> BatteryLevelData:
        """Parse battery level data (uint8 in percentage)."""
        if not data:
            raise ValueError("Battery level data must be at least 1 byte")

        # Convert uint8 to percentage
        level = data[0]
        return BatteryLevelData(level=level)

    def encode_value(self, data: BatteryLevelData) -> bytearray:
        """Encode BatteryLevelData back to bytes.

        Args:
            data: BatteryLevelData instance to encode

        Returns:
            Encoded bytes representing the battery level
        """
        return self._encode_uint8(data.level)
