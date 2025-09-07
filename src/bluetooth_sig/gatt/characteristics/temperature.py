"""Temperature characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class TemperatureData:
    """Parsed data from Temperature characteristic."""

    celsius: float
    unit: str = "°C"

    def __post_init__(self):
        """Validate temperature data."""
        # Validate realistic temperature range for Bluetooth sensors
        if not -273.15 <= self.celsius <= 1000.0:
            raise ValueError(f"Temperature {self.celsius}°C is outside realistic range (-273.15 to 1000°C)")
        if self.unit != "°C":
            raise ValueError(f"Temperature unit must be '°C', got {self.unit}")


@dataclass
class TemperatureCharacteristic(BaseCharacteristic):
    """Temperature measurement characteristic."""

    _characteristic_name: str = "Temperature"

    def parse_value(self, data: bytearray) -> TemperatureData:
        """Parse temperature data (sint16 in units of 0.01 degrees Celsius)."""
        if len(data) < 2:
            raise ValueError("Temperature data must be at least 2 bytes")

        # Convert sint16 (little endian) to temperature in Celsius
        temp_raw = self._parse_sint16(data, 0)
        celsius = temp_raw * 0.01
        return TemperatureData(celsius=celsius)

    def encode_value(self, data: TemperatureData) -> bytearray:
        """Encode TemperatureData back to bytes.

        Args:
            data: TemperatureData instance to encode

        Returns:
            Encoded bytes representing the temperature
        """
        # Convert Celsius to raw value (multiply by 100 for 0.01 resolution)
        temp_raw = round(data.celsius * 100)
        return self._encode_sint16(temp_raw)
