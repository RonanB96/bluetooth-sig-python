"""Apparent Wind Speed characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class ApparentWindSpeedCharacteristic(BaseCharacteristic):
    """Apparent Wind Speed measurement characteristic."""

    _characteristic_name: str = "Apparent Wind Speed"

    def parse_value(self, data: bytearray) -> float:
        """Parse apparent wind speed data (uint16 in units of 0.01 m/s)."""
        if len(data) < 2:
            raise ValueError("Apparent wind speed data must be at least 2 bytes")

        # Convert uint16 (little endian) to wind speed in m/s
        wind_speed_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return wind_speed_raw * 0.01
