"""Temperature characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class TemperatureCharacteristic(BaseCharacteristic):
    """Temperature measurement characteristic."""

    _characteristic_name: str = "Temperature"

    def parse_value(self, data: bytearray) -> float:
        """Parse temperature data (sint16 in units of 0.01 degrees Celsius)."""
        if len(data) < 2:
            raise ValueError("Temperature data must be at least 2 bytes")

        # Convert sint16 (little endian) to temperature in Celsius
        temp_raw = int.from_bytes(data[:2], byteorder="little", signed=True)
        return temp_raw * 0.01

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "°C"
