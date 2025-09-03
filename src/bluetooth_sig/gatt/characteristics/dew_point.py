"""Dew Point characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class DewPointCharacteristic(BaseCharacteristic):
    """Dew Point measurement characteristic."""

    _characteristic_name: str = "Dew Point"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse dew point data (sint8 in units of 1 degree Celsius)."""
        if len(data) < 1:
            raise ValueError("Dew point data must be at least 1 byte")

        # Convert sint8 to temperature in Celsius
        dew_point_raw = int.from_bytes(data[:1], byteorder="little", signed=True)
        return float(dew_point_raw)

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "°C"
