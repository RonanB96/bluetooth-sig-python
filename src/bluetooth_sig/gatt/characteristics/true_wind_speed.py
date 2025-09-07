"""True Wind Speed characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class TrueWindSpeedCharacteristic(BaseCharacteristic):
    """True Wind Speed measurement characteristic."""

    _characteristic_name: str = "True Wind Speed"

    def parse_value(self, data: bytearray) -> float:
        """Parse true wind speed data (uint16 in units of 0.01 m/s)."""
        if len(data) < 2:
            raise ValueError("True wind speed data must be at least 2 bytes")

        # Convert uint16 (little endian) to wind speed in m/s
        wind_speed_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return wind_speed_raw * 0.01

    def encode_value(self, data: float | int) -> bytearray:
        """Encode true wind speed value back to bytes.

        Args:
            data: True wind speed in m/s

        Returns:
            Encoded bytes representing the wind speed (uint16, 0.01 m/s resolution)
        """
        wind_speed = float(data)

        # Validate range (reasonable wind speed range)
        if not 0.0 <= wind_speed <= 655.35:  # Max uint16 * 0.01
            raise ValueError(
                f"True wind speed {wind_speed} m/s is outside valid range (0.0 to 655.35 m/s)"
            )

        # Convert m/s to raw value (multiply by 100 for 0.01 m/s resolution)
        wind_speed_raw = round(wind_speed * 100)

        return bytearray(wind_speed_raw.to_bytes(2, byteorder="little", signed=False))
