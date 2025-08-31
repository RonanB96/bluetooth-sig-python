"""Humidity characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class HumidityCharacteristic(BaseCharacteristic):
    """Humidity measurement characteristic."""

    _characteristic_name: str = "Humidity"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse humidity data (uint16 in units of 0.01 percent)."""
        if len(data) < 2:
            raise ValueError("Humidity data must be at least 2 bytes")

        # Convert uint16 (little endian) to humidity percentage
        humidity_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return humidity_raw * 0.01

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "%"

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "humidity"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "measurement"
