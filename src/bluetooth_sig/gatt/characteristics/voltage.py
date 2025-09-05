"""Voltage characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class VoltageCharacteristic(BaseCharacteristic):
    """Voltage characteristic.

    Measures voltage with 1/64 V resolution.
    """

    _characteristic_name: str = "Voltage"

    def parse_value(self, data: bytearray) -> float:
        """Parse voltage data (uint16 in units of 1/64 V).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            Voltage value in Volts

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 2:
            raise ValueError("Voltage data must be at least 2 bytes")

        # Convert uint16 (little endian) to voltage in Volts
        voltage_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return voltage_raw / 64.0

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "V"
