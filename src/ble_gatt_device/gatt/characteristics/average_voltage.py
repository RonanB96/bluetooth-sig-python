"""Average Voltage characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class AverageVoltageCharacteristic(BaseCharacteristic):
    """Average Voltage characteristic.
    
    Measures average voltage with 1/64 V resolution.
    """

    _characteristic_name: str = "Average Voltage"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse average voltage data (uint16 in units of 1/64 V).
        
        Args:
            data: Raw bytes from the characteristic read
            
        Returns:
            Average voltage value in Volts
            
        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 2:
            raise ValueError("Average voltage data must be at least 2 bytes")

        # Convert uint16 (little endian) to voltage in Volts
        voltage_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return voltage_raw / 64.0

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