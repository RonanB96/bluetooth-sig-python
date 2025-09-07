"""Humidity characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class HumidityData:
    """Parsed data from Humidity characteristic."""

    humidity: float
    unit: str = "%"

    def __post_init__(self):
        """Validate humidity data."""
        if not 0.0 <= self.humidity <= 100.0:
            raise ValueError(f"Humidity must be 0.0-100.0%, got {self.humidity}")
        if self.unit != "%":
            raise ValueError(f"Humidity unit must be '%', got {self.unit}")

    def __eq__(self, other) -> bool:
        """Support comparison with float values for backward compatibility."""
        if isinstance(other, (int, float)):
            return abs(self.humidity - other) < 1e-9  # Float comparison with tolerance
        return super().__eq__(other)

    def __float__(self) -> float:
        """Support float conversion for backward compatibility."""
        return self.humidity

    def __str__(self) -> str:
        """String representation showing the humidity."""
        return str(self.humidity)


@dataclass
class HumidityCharacteristic(BaseCharacteristic):
    """Humidity measurement characteristic."""

    _characteristic_name: str = "Humidity"
    _manual_value_type: str = (
        "float"  # Override YAML int type since parse_value returns float
    )

    def parse_value(self, data: bytearray) -> HumidityData:
        """Parse humidity data (uint16 in units of 0.01 percent)."""
        if len(data) < 2:
            raise ValueError("Humidity data must be at least 2 bytes")

        # Convert uint16 (little endian) to humidity percentage
        humidity_raw = self._parse_uint16(data, 0)
        humidity = humidity_raw * 0.01
        return HumidityData(humidity=humidity)

    def encode_value(self, data: HumidityData) -> bytearray:
        """Encode HumidityData back to bytes.

        Args:
            data: HumidityData instance to encode

        Returns:
            Encoded bytes representing the humidity
        """
        # Convert percentage to raw value (multiply by 100 for 0.01 resolution)
        humidity_raw = round(data.humidity * 100)
        return self._encode_uint16(humidity_raw)
