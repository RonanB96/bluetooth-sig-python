"""True Wind Direction characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class TrueWindDirectionCharacteristic(BaseCharacteristic):
    """True Wind Direction measurement characteristic."""

    _characteristic_name: str = "True Wind Direction"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse true wind direction data (uint16 in units of 0.01 degrees)."""
        if len(data) < 2:
            raise ValueError("True wind direction data must be at least 2 bytes")

        # Convert uint16 (little endian) to wind direction in degrees
        wind_direction_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return wind_direction_raw * 0.01

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "°"
