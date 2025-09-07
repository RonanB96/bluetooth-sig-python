"""Rainfall characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class RainfallCharacteristic(BaseCharacteristic):
    """Rainfall characteristic.

    Represents the amount of rain that has fallen in millimeters.
    """

    _characteristic_name: str = "Rainfall"

    def decode_value(self, data: bytearray) -> float:
        """Parse rainfall data (uint16 in meters with 1mm resolution)."""
        if len(data) < 2:
            raise ValueError("Rainfall data must be at least 2 bytes")

        # Convert uint16 (little endian) to millimeters
        # Specification says "meters with a resolution of 1mm" which means
        # the value is in 0.001 meter units (millimeters)
        rainfall_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return float(rainfall_raw)  # Already in millimeters

    def encode_value(self, data: float | int) -> bytearray:
        """Encode rainfall value back to bytes.

        Args:
            data: Rainfall in millimeters

        Returns:
            Encoded bytes representing the rainfall (uint16, 1 mm resolution)
        """
        rainfall = float(data)

        # Validate range (reasonable rainfall range)
        if not 0.0 <= rainfall <= 65535.0:  # Max uint16 for mm
            raise ValueError(
                f"Rainfall {rainfall} mm is outside valid range (0.0 to 65535.0 mm)"
            )

        # Convert to raw value (already in millimeters)
        rainfall_raw = round(rainfall)

        return bytearray(rainfall_raw.to_bytes(2, byteorder="little", signed=False))

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "mm"
