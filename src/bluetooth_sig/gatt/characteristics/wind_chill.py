"""Wind Chill characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class WindChillCharacteristic(BaseCharacteristic):
    """Wind Chill measurement characteristic."""

    _characteristic_name: str = "Wind Chill"

    def parse_value(self, data: bytearray) -> float:
        """Parse wind chill data (sint8 in units of 1 degree Celsius)."""
        if len(data) < 1:
            raise ValueError("Wind chill data must be at least 1 byte")

        # Convert sint8 to temperature in Celsius
        wind_chill_raw = int.from_bytes(data[:1], byteorder="little", signed=True)
        return float(wind_chill_raw)

    def encode_value(self, data) -> bytearray:
        """Encode value back to bytes - basic stub implementation."""
        # TODO: Implement proper encoding
        raise NotImplementedError(
            "encode_value not yet implemented for this characteristic"
        )

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "°C"
