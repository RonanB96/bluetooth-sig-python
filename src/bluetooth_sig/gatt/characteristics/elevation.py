"""Elevation characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class ElevationCharacteristic(BaseCharacteristic):
    """Elevation characteristic.

    Represents the elevation relative to sea level unless otherwise
    specified in the service.
    """

    _characteristic_name: str = "Elevation"
    _manual_value_type: str = (
        "float"  # Override YAML int type since parse_value returns float
    )

    def parse_value(self, data: bytearray) -> float:
        """Parse elevation data (sint24 in units of 0.01 meters)."""
        if len(data) < 3:
            raise ValueError("Elevation data must be at least 3 bytes")

        # Parse sint24 (little endian) - need to handle 24-bit signed integer
        # Convert to 32-bit first for proper sign extension
        raw_bytes = data[:3] + b"\x00"  # Pad to 4 bytes
        elevation_raw = int.from_bytes(raw_bytes, byteorder="little", signed=False)

        # Handle sign extension for 24-bit signed value
        if elevation_raw & 0x800000:  # Check if negative (bit 23 set)
            elevation_raw = elevation_raw - 0x1000000  # Convert to negative

        return elevation_raw * 0.01  # Convert to meters
