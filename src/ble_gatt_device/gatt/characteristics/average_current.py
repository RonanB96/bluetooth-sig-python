"""Average Current characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class AverageCurrentCharacteristic(BaseCharacteristic):
    """Average Current characteristic.

    Measures average electric current with 0.01 A resolution.
    """

    _characteristic_name: str = "Average Current"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse average current data (uint16 in units of 0.01 A).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            Average current value in Amperes

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 2:
            raise ValueError("Average current data must be at least 2 bytes")

        # Convert uint16 (little endian) to current in Amperes
        current_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return current_raw * 0.01

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "A"

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "current"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "measurement"
