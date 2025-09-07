"""Humidity characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class HumidityCharacteristic(BaseCharacteristic):
    """Humidity measurement characteristic."""

    _characteristic_name: str = "Humidity"
    _manual_value_type: str = (
        "float"  # Override YAML int type since parse_value returns float
    )

    def parse_value(self, data: bytearray) -> float:
        """Parse humidity data (uint16 in units of 0.01 percent)."""
        if len(data) < 2:
            raise ValueError("Humidity data must be at least 2 bytes")

        # Convert uint16 (little endian) to humidity percentage
        humidity_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return humidity_raw * 0.01


    def encode_value(self, data) -> bytearray:
        """Encode value back to bytes - basic stub implementation."""
        # TODO: Implement proper encoding
        raise NotImplementedError("encode_value not yet implemented for this characteristic")