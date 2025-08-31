"""High Voltage characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class HighVoltageCharacteristic(BaseCharacteristic):
    """High Voltage characteristic.
    
    Measures high voltage systems using uint24 format.
    """

    _characteristic_name: str = "High Voltage"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse high voltage data (uint24 for high voltage systems).
        
        Args:
            data: Raw bytes from the characteristic read
            
        Returns:
            High voltage value in Volts
            
        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 3:
            raise ValueError("High voltage data must be at least 3 bytes")

        # Convert uint24 (little endian) to voltage in Volts
        # Add padding byte for uint32 conversion
        voltage_data = data[:3] + b'\x00'
        voltage_raw = int.from_bytes(voltage_data, byteorder="little", signed=False)
        return float(voltage_raw)

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "V"

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "voltage"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "measurement"