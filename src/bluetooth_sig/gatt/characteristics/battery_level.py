"""Battery level characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class BatteryLevelCharacteristic(BaseCharacteristic):
    """Battery level characteristic."""

    _characteristic_name: str = "Battery Level"
    _manual_unit: str = "%"  # Ensure unit is set correctly

    def parse_value(self, data: bytearray) -> int:
        """Parse battery level data (uint8 in percentage)."""
        if not data:
            raise ValueError("Battery level data must be at least 1 byte")

        # Convert uint8 to percentage
        return data[0]
