"""Electric Current Statistics characteristic implementation."""

from dataclasses import dataclass
from typing import Dict

from .base import BaseCharacteristic


@dataclass
class ElectricCurrentStatisticsCharacteristic(BaseCharacteristic):
    """Electric Current Statistics characteristic.
    
    Provides statistical current data (min, max, average over time).
    """

    _characteristic_name: str = "Electric Current Statistics"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "dict"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> Dict[str, float]:
        """Parse current statistics data (3x uint16 in units of 0.01 A).
        
        Args:
            data: Raw bytes from the characteristic read
            
        Returns:
            Dictionary with 'minimum', 'maximum', and 'average' current values in Amperes
            
        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 6:
            raise ValueError("Electric current statistics data must be at least 6 bytes")

        # Convert 3x uint16 (little endian) to current statistics in Amperes
        min_current_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        max_current_raw = int.from_bytes(data[2:4], byteorder="little", signed=False)
        avg_current_raw = int.from_bytes(data[4:6], byteorder="little", signed=False)
        
        return {
            "minimum": min_current_raw * 0.01,
            "maximum": max_current_raw * 0.01,
            "average": avg_current_raw * 0.01
        }

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "A"

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "current"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return ""  # Statistical data doesn't have a standard state class