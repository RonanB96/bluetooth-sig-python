"""Illuminance characteristic implementation."""

import struct
from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class IlluminanceCharacteristic(BaseCharacteristic):
    """Illuminance characteristic (0x2AFB).
    
    Measures light intensity in lux (lumens per square meter).
    """

    _characteristic_name: str = "Illuminance"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse illuminance data.
        
        Format: 3-byte value representing illuminance in 0.01 lux units.
        
        Args:
            data: Raw bytearray from BLE characteristic
            
        Returns:
            Illuminance value in lux
        """
        if len(data) < 3:
            raise ValueError("Illuminance data must be at least 3 bytes")

        # Convert 3-byte unsigned integer (little endian) to illuminance in lux
        illuminance_raw = int.from_bytes(data[:3], byteorder="little", signed=False)
        return illuminance_raw * 0.01

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "lx"

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "illuminance"
        
    @property 
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "measurement"