"""Pollen Concentration characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class PollenConcentrationCharacteristic(BaseCharacteristic):
    """Pollen concentration characteristic.

    Represents the pollen count in count per cubic meter.
    """

    _characteristic_name: str = "Pollen Concentration"

    def decode_value(self, data: bytearray) -> int:
        """Parse pollen concentration data (uint24 in count per cubic meter)."""
        if len(data) < 3:
            raise ValueError("Pollen concentration data must be at least 3 bytes")

        # Parse uint24 (little endian) - pad to 4 bytes for parsing
        raw_bytes = data[:3] + b"\x00"  # Pad to 4 bytes
        concentration = int.from_bytes(raw_bytes, byteorder="little", signed=False)

        return concentration

    def encode_value(self, data: int) -> bytearray:
        """Encode pollen concentration value back to bytes.

        Args:
            data: Pollen concentration in count/m³

        Returns:
            Encoded bytes representing the pollen concentration (uint24, 1 count/m³ resolution)
        """
        concentration = int(data)

        # Validate range for uint24 (0 to 16777215)
        if not 0 <= concentration <= 16777215:
            raise ValueError(
                f"Pollen concentration {concentration} count/m³ is outside valid range (0-16777215 count/m³)"
            )

        # Encode as 3 bytes (little endian)
        return bytearray(concentration.to_bytes(3, byteorder="little", signed=False))

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "count/m³"
