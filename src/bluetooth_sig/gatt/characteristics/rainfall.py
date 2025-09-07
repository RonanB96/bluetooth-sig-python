"""Rainfall characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class RainfallCharacteristic(BaseCharacteristic):
    """Rainfall characteristic.

    Represents the amount of rain that has fallen in millimeters.
    """

    _characteristic_name: str = "Rainfall"

    def parse_value(self, data: bytearray) -> float:
        """Parse rainfall data (uint16 in meters with 1mm resolution)."""
        if len(data) < 2:
            raise ValueError("Rainfall data must be at least 2 bytes")

        # Convert uint16 (little endian) to millimeters
        # Specification says "meters with a resolution of 1mm" which means
        # the value is in 0.001 meter units (millimeters)
        rainfall_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return float(rainfall_raw)  # Already in millimeters


    def encode_value(self, data) -> bytearray:
        """Encode value back to bytes - basic stub implementation."""
        # TODO: Implement proper encoding
        raise NotImplementedError("encode_value not yet implemented for this characteristic")
    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "mm"
