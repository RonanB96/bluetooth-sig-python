"""Pollen Concentration characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class PollenConcentrationCharacteristic(BaseCharacteristic):
    """Pollen concentration characteristic.

    Represents the pollen count in count per cubic meter.
    """

    _characteristic_name: str = "Pollen Concentration"

    def parse_value(self, data: bytearray) -> int:
        """Parse pollen concentration data (uint24 in count per cubic meter)."""
        if len(data) < 3:
            raise ValueError("Pollen concentration data must be at least 3 bytes")

        # Parse uint24 (little endian) - pad to 4 bytes for parsing
        raw_bytes = data[:3] + b"\x00"  # Pad to 4 bytes
        concentration = int.from_bytes(raw_bytes, byteorder="little", signed=False)

        return concentration


    def encode_value(self, data) -> bytearray:
        """Encode value back to bytes - basic stub implementation."""
        # TODO: Implement proper encoding
        raise NotImplementedError("encode_value not yet implemented for this characteristic")
    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "count/m³"
