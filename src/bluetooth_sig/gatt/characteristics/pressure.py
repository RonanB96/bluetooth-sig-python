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
        return pressure_raw * 0.001  # Convert Pa to kPa

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "kPa"

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "pressure"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "measurement"
