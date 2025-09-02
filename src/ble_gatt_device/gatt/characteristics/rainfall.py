"""Rainfall characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class RainfallCharacteristic(BaseCharacteristic):
    """Rainfall characteristic.

    Represents the amount of rain that has fallen in millimeters.
    """

    _characteristic_name: str = "Rainfall"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse rainfall data (uint16 in meters with 1mm resolution)."""
        if len(data) < 2:
            raise ValueError("Rainfall data must be at least 2 bytes")

        # Convert uint16 (little endian) to millimeters
        # Specification says "meters with a resolution of 1mm" which means
        # the value is in 0.001 meter units (millimeters)
        rainfall_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return float(rainfall_raw)  # Already in millimeters

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "mm"

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "precipitation"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "total_increasing"  # Rainfall accumulates over time
