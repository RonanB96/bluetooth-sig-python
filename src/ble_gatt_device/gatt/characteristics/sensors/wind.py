"""Wind sensor characteristic implementations."""

from dataclasses import dataclass

from ..base import BaseCharacteristic


@dataclass
class ApparentWindDirectionCharacteristic(BaseCharacteristic):
    """Apparent Wind Direction characteristic (UUID: 0x2A73).
    
    Measures wind direction in degrees according to Bluetooth SIG specification.
    Data format: uint16 representing direction in 0.01 degree resolution.
    """

    _characteristic_name: str = "Apparent Wind Direction"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse wind direction data (uint16 in units of 0.01 degrees).
        
        Args:
            data: Raw byte data from BLE characteristic
            
        Returns:
            Wind direction in degrees (0-360)
            
        Raises:
            ValueError: If data is insufficient or malformed
        """
        if len(data) < 2:
            raise ValueError("Wind direction data must be at least 2 bytes")

        # Convert uint16 (little endian) to direction in degrees
        direction_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        direction = direction_raw * 0.01
        
        # Ensure direction is within 0-360 range
        return direction % 360.0

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "°"


@dataclass
class ApparentWindSpeedCharacteristic(BaseCharacteristic):
    """Apparent Wind Speed characteristic (UUID: 0x2A72).
    
    Measures wind speed in m/s according to Bluetooth SIG specification.
    Data format: uint16 representing speed in 0.01 m/s resolution.
    """

    _characteristic_name: str = "Apparent Wind Speed"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse wind speed data (uint16 in units of 0.01 m/s).
        
        Args:
            data: Raw byte data from BLE characteristic
            
        Returns:
            Wind speed in m/s
            
        Raises:
            ValueError: If data is insufficient or malformed
        """
        if len(data) < 2:
            raise ValueError("Wind speed data must be at least 2 bytes")

        # Convert uint16 (little endian) to speed in m/s
        speed_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return speed_raw * 0.01

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "m/s"