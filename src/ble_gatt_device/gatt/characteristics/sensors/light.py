"""Light/Illuminance sensor characteristic implementation."""

from dataclasses import dataclass

from ..base import BaseCharacteristic


@dataclass
class IlluminanceCharacteristic(BaseCharacteristic):
    """Illuminance measurement characteristic (UUID: 0x2AFB).
    
    Measures ambient light levels in lux according to Bluetooth SIG specification.
    Data format: uint24 representing illuminance in 0.01 lux resolution.
    """

    _characteristic_name: str = "Illuminance"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse illuminance data (uint24 in units of 0.01 lux).
        
        Args:
            data: Raw byte data from BLE characteristic
            
        Returns:
            Illuminance value in lux
            
        Raises:
            ValueError: If data is insufficient or malformed
        """
        if len(data) < 3:
            raise ValueError("Illuminance data must be at least 3 bytes")

        # Convert uint24 (little endian) to illuminance in lux
        illuminance_raw = int.from_bytes(data[:3], byteorder="little", signed=False)
        return illuminance_raw * 0.01

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "lx"