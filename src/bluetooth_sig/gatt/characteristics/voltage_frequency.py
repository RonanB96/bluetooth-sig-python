"""Voltage Frequency characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class VoltageFrequencyCharacteristic(BaseCharacteristic):
    """Voltage Frequency characteristic.

    Measures voltage frequency with 1/256 Hz resolution.
    """

    _characteristic_name: str = "Voltage Frequency"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse voltage frequency data (uint16 in units of 1/256 Hz).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            Frequency value in Hz

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 2:
            raise ValueError("Voltage frequency data must be at least 2 bytes")

        # Convert uint16 (little endian) to frequency in Hz
        frequency_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return frequency_raw / 256.0

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "Hz"
