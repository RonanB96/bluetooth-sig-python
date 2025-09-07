"""Heat Index characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class HeatIndexCharacteristic(BaseCharacteristic):
    """Heat Index measurement characteristic."""

    _characteristic_name: str = "Heat Index"

    def parse_value(self, data: bytearray) -> float:
        """Parse heat index data (uint8 in units of 1 degree Celsius)."""
        if len(data) < 1:
            raise ValueError("Heat index data must be at least 1 byte")

        # Convert uint8 to temperature in Celsius
        heat_index_raw = int.from_bytes(data[:1], byteorder="little", signed=False)
        return float(heat_index_raw)

    def encode_value(self, data: float | int) -> bytearray:
        """Encode heat index value back to bytes.

        Args:
            data: Heat index temperature in Celsius

        Returns:
            Encoded bytes representing the heat index (uint8, 1°C resolution)
        """
        temperature = int(round(float(data)))

        # Validate range for uint8 (0 to 255)
        if not 0 <= temperature <= 255:
            raise ValueError(
                f"Heat index {temperature}°C is outside valid range (0 to 255°C)"
            )

        return bytearray(temperature.to_bytes(1, byteorder="little", signed=False))

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "°C"
