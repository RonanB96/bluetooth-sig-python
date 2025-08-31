"""Sound Pressure Level characteristic implementation."""

import struct
from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class SoundPressureLevelCharacteristic(BaseCharacteristic):
    """Sound Pressure Level characteristic (0x2B06).
    
    Measures sound pressure level in decibels (dB).
    """

    _characteristic_name: str = "Sound Pressure Level"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse sound pressure level data.
        
        Format: 2-byte signed integer representing sound level in 0.1 dB units.
        
        Args:
            data: Raw bytearray from BLE characteristic
            
        Returns:
            Sound pressure level in dB
        """
        if len(data) < 2:
            raise ValueError("Sound Pressure Level data must be at least 2 bytes")

        # Convert sint16 (little endian) to sound level in dB
        spl_raw = int.from_bytes(data[:2], byteorder="little", signed=True)
        return spl_raw * 0.1

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "dB"

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "sound_pressure"
        
    @property 
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "measurement"