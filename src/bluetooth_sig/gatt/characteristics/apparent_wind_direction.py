"""Apparent Wind Direction characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class ApparentWindDirectionCharacteristic(BaseCharacteristic):
    """Apparent Wind Direction measurement characteristic."""

    _characteristic_name: str = "Apparent Wind Direction"

    def parse_value(self, data: bytearray) -> float:
        """Parse apparent wind direction data (uint16 in units of 0.01 degrees)."""
        if len(data) < 2:
            raise ValueError("Apparent wind direction data must be at least 2 bytes")

        # Convert uint16 (little endian) to wind direction in degrees
        wind_direction_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return wind_direction_raw * 0.01
