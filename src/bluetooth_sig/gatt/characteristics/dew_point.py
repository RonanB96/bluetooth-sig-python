"""Dew Point characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class DewPointCharacteristic(BaseCharacteristic):
    """Dew Point measurement characteristic."""

    _characteristic_name: str = "Dew Point"

    def parse_value(self, data: bytearray) -> float:
        """Parse dew point data (sint8 in units of 1 degree Celsius)."""
        if len(data) < 1:
            raise ValueError("Dew point data must be at least 1 byte")

        # Convert sint8 to temperature in Celsius
        dew_point_raw = int.from_bytes(data[:1], byteorder="little", signed=True)
        return float(dew_point_raw)

    def encode_value(self, data: float | int) -> bytearray:
        """Encode dew point value back to bytes.

        Args:
            data: Dew point temperature in Celsius

        Returns:
            Encoded bytes representing the dew point (sint8, 1°C resolution)
        """
        temperature = int(round(float(data)))

        # Validate range for sint8 (-128 to 127)
        if not -128 <= temperature <= 127:
            raise ValueError(
                f"Dew point {temperature}°C is outside valid range (-128 to 127°C)"
            )

        return bytearray(temperature.to_bytes(1, byteorder="little", signed=True))
