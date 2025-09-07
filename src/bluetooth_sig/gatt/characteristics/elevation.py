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
        "float"  # Override YAML int type since decode_value returns float
    )

    def decode_value(self, data: bytearray) -> float:
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

    def encode_value(self, data: float | int) -> bytearray:
        """Encode elevation value back to bytes.

        Args:
            data: Elevation value in meters

        Returns:
            Encoded bytes representing the elevation (sint24, 0.01 m resolution)
        """
        elevation_m = float(data)

        # Validate range (reasonable elevation range)
        if not -10000 <= elevation_m <= 10000:  # -10km to 10km
            raise ValueError(
                f"Elevation {elevation_m} m is outside valid range (-10000 to 10000 m)"
            )

        # Convert meters to raw value (multiply by 100 for 0.01 m resolution)
        elevation_raw = round(elevation_m * 100)

        # Ensure it fits in sint24 range (-8388608 to 8388607)
        if not -8388608 <= elevation_raw <= 8388607:
            raise ValueError(f"Elevation value {elevation_raw} exceeds sint24 range")

        # Convert to unsigned representation for encoding
        if elevation_raw < 0:
            elevation_unsigned = (
                elevation_raw + 0x1000000
            )  # Convert negative to 24-bit unsigned
        else:
            elevation_unsigned = elevation_raw

        # Encode as 3 bytes (little endian)
        return bytearray(
            elevation_unsigned.to_bytes(3, byteorder="little", signed=False)
        )
