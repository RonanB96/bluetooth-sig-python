"""Battery level characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class BatteryLevelCharacteristic(BaseCharacteristic):
    """Battery level characteristic."""

    _characteristic_name: str = "Battery Level"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "int"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> int:
        """Parse battery level data (uint8 in percentage)."""
        if not data:
            raise ValueError("Battery level data must be at least 1 byte")

        # Convert uint8 to percentage
        return data[0]

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "%"

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "battery"
        
    @property 
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "measurement"
