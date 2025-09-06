"""Pressure characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class PressureCharacteristic(BaseCharacteristic):
    """Atmospheric pressure characteristic."""

    _characteristic_name: str = "Pressure"

    def parse_value(self, data: bytearray) -> float:
        """Parse pressure data (uint32 in units of 0.1 Pa)."""
        if len(data) < 4:
            raise ValueError("Pressure data must be at least 4 bytes")

        # Convert uint32 (little endian) to pressure in Pa
        pressure_raw = int.from_bytes(data[:4], byteorder="little", signed=False)
        return pressure_raw * 0.1  # Convert to Pa with 0.1 Pa resolution

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "Pa"
