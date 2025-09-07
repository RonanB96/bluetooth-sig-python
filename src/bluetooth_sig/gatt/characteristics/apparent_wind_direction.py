"""Apparent Wind Direction characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class ApparentWindDirectionCharacteristic(BaseCharacteristic):
    """Apparent Wind Direction measurement characteristic."""

    _characteristic_name: str = "Apparent Wind Direction"

    def parse_value(self, data: bytearray) -> float:
        """Parse apparent wind direction data (uint16 in units of 0.01 degrees)."""
        if len(data) < 2:
            raise ValueError("Apparent wind direction data must be at least 2 bytes")

        # Convert uint16 (little endian) to wind direction in degrees
        wind_direction_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return wind_direction_raw * 0.01

    def encode_value(self, data: float | int) -> bytearray:
        """Encode apparent wind direction value back to bytes.

        Args:
            data: Apparent wind direction in degrees

        Returns:
            Encoded bytes representing the wind direction (uint16, 0.01 degrees resolution)
        """
        wind_direction = float(data) % 360.0  # Normalize to 0-360 degrees

        # Validate range (0 to 359.99 degrees)
        if not 0.0 <= wind_direction < 360.0:
            raise ValueError(
                f"Apparent wind direction {wind_direction}° is outside valid range (0.0 to 359.99°)"
            )

        # Convert degrees to raw value (multiply by 100 for 0.01 degree resolution)
        wind_direction_raw = round(wind_direction * 100)

        # Ensure it fits in uint16
        if wind_direction_raw > 65535:  # pylint: disable=consider-using-min-builtin # Clear intent for range clamping
            wind_direction_raw = 65535

        return bytearray(
            wind_direction_raw.to_bytes(2, byteorder="little", signed=False)
        )
