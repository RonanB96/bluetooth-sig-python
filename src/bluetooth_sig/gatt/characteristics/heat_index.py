"""Heat Index characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class HeatIndexCharacteristic(BaseCharacteristic):
    """Heat Index measurement characteristic."""

    _characteristic_name: str = "Heat Index"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse heat index data (uint8 in units of 1 degree Celsius)."""
        if len(data) < 1:
            raise ValueError("Heat index data must be at least 1 byte")

        # Convert uint8 to temperature in Celsius
        heat_index_raw = int.from_bytes(data[:1], byteorder="little", signed=False)
        return float(heat_index_raw)

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "°C"
