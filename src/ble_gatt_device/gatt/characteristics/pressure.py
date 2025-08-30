"""Pressure characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class PressureCharacteristic(BaseCharacteristic):
    """Atmospheric pressure characteristic."""

    _characteristic_name: str = "Pressure"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse pressure data (uint32 in units of 0.1 Pa)."""
        if len(data) < 4:
            raise ValueError("Pressure data must be at least 4 bytes")

        # Convert uint32 (little endian) to pressure in hPa
        pressure_raw = int.from_bytes(data[:4], byteorder="little", signed=False)
        return pressure_raw * 0.01  # Convert 0.1 Pa to hPa

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "hPa"
