"""Sound level sensor characteristic implementation."""

from dataclasses import dataclass

from ..base import BaseCharacteristic


@dataclass
class SoundLevelCharacteristic(BaseCharacteristic):
    """Sound pressure level measurement characteristic (UUID: 0x2B28).
    
    Measures sound pressure level in decibels A-weighted (dBA) according to 
    Bluetooth SIG specification. Data format: uint8 representing sound level 
    in 1 dBA resolution.
    """

    _characteristic_name: str = "Sound Pressure Level"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse sound level data (uint8 in units of 1 dBA).
        
        Args:
            data: Raw byte data from BLE characteristic
            
        Returns:
            Sound pressure level in dBA
            
        Raises:
            ValueError: If data is insufficient or malformed
        """
        if len(data) < 1:
            raise ValueError("Sound level data must be at least 1 byte")

        # Convert uint8 to sound level in dBA
        sound_level = int.from_bytes(data[:1], byteorder="little", signed=False)
        return float(sound_level)

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "dBA"