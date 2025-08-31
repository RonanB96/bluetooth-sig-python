"""Voltage Statistics characteristic implementation."""

from dataclasses import dataclass
from typing import Dict

from .base import BaseCharacteristic


@dataclass
class VoltageStatisticsCharacteristic(BaseCharacteristic):
    """Voltage Statistics characteristic.

    Provides statistical voltage data over time.
    """

    _characteristic_name: str = "Voltage Statistics"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "dict"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> Dict[str, float]:
        """Parse voltage statistics data (3x uint16 in units of 1/64 V).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            Dictionary with 'minimum', 'maximum', and 'average' voltage values in Volts

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 6:
            raise ValueError("Voltage statistics data must be at least 6 bytes")

        # Convert 3x uint16 (little endian) to voltage statistics in Volts
        min_voltage_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        max_voltage_raw = int.from_bytes(data[2:4], byteorder="little", signed=False)
        avg_voltage_raw = int.from_bytes(data[4:6], byteorder="little", signed=False)

        return {
            "minimum": min_voltage_raw / 64.0,
            "maximum": max_voltage_raw / 64.0,
            "average": avg_voltage_raw / 64.0,
        }

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
        return ""  # Statistical data doesn't have a standard state class
