"""Wind Chill characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class WindChillCharacteristic(BaseCharacteristic):
    """Wind Chill measurement characteristic."""

    _characteristic_name: str = "Wind Chill"

    def decode_value(self, data: bytearray) -> float:
        """Parse wind chill data (sint8 in units of 1 degree Celsius)."""
        if len(data) < 1:
            raise ValueError("Wind chill data must be at least 1 byte")

        # Convert sint8 to temperature in Celsius
        wind_chill_raw = int.from_bytes(data[:1], byteorder="little", signed=True)
        return float(wind_chill_raw)

    def encode_value(self, data: float | int) -> bytearray:
        """Encode wind chill value back to bytes.

        Args:
            data: Wind chill temperature in Celsius

        Returns:
            Encoded bytes representing the wind chill (sint8, 1°C resolution)
        """
        temperature = int(round(float(data)))

        # Validate range for sint8 (-128 to 127)
        if not -128 <= temperature <= 127:
            raise ValueError(
                f"Wind chill {temperature}°C is outside valid range (-128 to 127°C)"
            )

        return bytearray(temperature.to_bytes(1, byteorder="little", signed=True))

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "°C"
