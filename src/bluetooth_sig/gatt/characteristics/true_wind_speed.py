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


    def encode_value(self, data) -> bytearray:
        """Encode value back to bytes - basic stub implementation."""
        # TODO: Implement proper encoding
        raise NotImplementedError("encode_value not yet implemented for this characteristic")