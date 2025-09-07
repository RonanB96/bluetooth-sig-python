"""Electric Current characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class ElectricCurrentCharacteristic(BaseCharacteristic):
    """Electric Current characteristic.

    Measures electric current with 0.01 A resolution.
    """

    _characteristic_name: str = "Electric Current"

    def parse_value(self, data: bytearray) -> float:
        """Parse electric current data (uint16 in units of 0.01 A).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            Current value in Amperes

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 2:
            raise ValueError("Electric current data must be at least 2 bytes")

        # Convert uint16 (little endian) to current in Amperes
        current_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return current_raw * 0.01

    def encode_value(self, data) -> bytearray:
        """Encode value back to bytes - basic stub implementation."""
        # TODO: Implement proper encoding
        raise NotImplementedError(
            "encode_value not yet implemented for this characteristic"
        )

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "A"
