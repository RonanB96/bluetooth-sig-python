"""Voltage Frequency characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class VoltageFrequencyCharacteristic(BaseCharacteristic):
    """Voltage Frequency characteristic.

    Measures voltage frequency with 1/256 Hz resolution.
    """

    _characteristic_name: str = "Voltage Frequency"

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

    def encode_value(self, data) -> bytearray:
        """Encode value back to bytes - basic stub implementation."""
        # TODO: Implement proper encoding
        raise NotImplementedError(
            "encode_value not yet implemented for this characteristic"
        )

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "Hz"
