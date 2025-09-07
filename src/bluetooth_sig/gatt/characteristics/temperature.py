"""Temperature characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseCharacteristic
from .utils import DataParser


@dataclass
class TemperatureCharacteristic(BaseCharacteristic):
    """Temperature measurement characteristic."""

    _characteristic_name: str = "Temperature"

    def decode_value(self, data: bytearray) -> float:
        """Parse temperature data (sint16 in units of 0.01 degrees Celsius)."""
        if len(data) < 2:
            raise ValueError("Temperature data must be at least 2 bytes")

        # Convert sint16 (little endian) to temperature in Celsius
        temp_raw = DataParser.parse_sint16(data, 0)
        celsius = temp_raw * 0.01

        # Validate realistic temperature range for Bluetooth sensors
        if not -273.15 <= celsius <= 1000.0:
            raise ValueError(
                f"Temperature {celsius}°C is outside realistic range (-273.15 to 1000°C)"
            )

        return celsius

    def encode_value(self, data: float | int) -> bytearray:
        """Encode temperature value back to bytes.

        Args:
            data: Temperature value in Celsius

        Returns:
            Encoded bytes representing the temperature
        """
        celsius = float(data)

        # Validate range
        if not -273.15 <= celsius <= 1000.0:
            raise ValueError(
                f"Temperature {celsius}°C is outside realistic range (-273.15 to 1000°C)"
            )

        # Convert Celsius to raw value (multiply by 100 for 0.01 resolution)
        temp_raw = round(celsius * 100)
        return DataParser.encode_sint16(temp_raw)
