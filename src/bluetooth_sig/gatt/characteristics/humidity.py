"""Humidity characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseCharacteristic
from .utils import DataParser


@dataclass
class HumidityCharacteristic(BaseCharacteristic):
    """Humidity measurement characteristic."""

    _characteristic_name: str = "Humidity"
    _manual_value_type: str = (
        "float"  # Override YAML int type since decode_value returns float
    )

    def decode_value(self, data: bytearray) -> float:
        """Parse humidity data (uint16 in units of 0.01 percent)."""
        if len(data) < 2:
            raise ValueError("Humidity data must be at least 2 bytes")

        # Convert uint16 (little endian) to humidity percentage
        humidity_raw = DataParser.parse_uint16(data, 0)
        humidity = humidity_raw * 0.01

        # Validate range
        if not 0.0 <= humidity <= 100.0:
            raise ValueError(f"Humidity must be 0.0-100.0%, got {humidity}")

        return humidity

    def encode_value(self, data: float | int) -> bytearray:
        """Encode humidity value back to bytes.

        Args:
            data: Humidity value as percentage (0.0-100.0)

        Returns:
            Encoded bytes representing the humidity
        """
        humidity = float(data)

        # Validate range
        if not 0.0 <= humidity <= 100.0:
            raise ValueError(f"Humidity must be 0.0-100.0%, got {humidity}")

        # Convert percentage to raw value (multiply by 100 for 0.01 resolution)
        humidity_raw = round(humidity * 100)
        return DataParser.encode_uint16(humidity_raw)
