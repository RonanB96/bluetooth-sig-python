"""UV Index characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class UVIndexCharacteristic(BaseCharacteristic):
    """UV Index characteristic."""

    _characteristic_name: str = "UV Index"
    # YAML provides uint8 -> int, which is correct for UV Index values (0-11+ scale)

    def parse_value(self, data: bytearray) -> int:
        """Parse UV Index data (uint8)."""
        if len(data) < 1:
            raise ValueError("UV Index data must be at least 1 byte")

        # UV Index is a uint8 value (0-11+ scale)
        return data[0]

    def encode_value(self, data: int) -> bytearray:
        """Encode UV index value back to bytes.

        Args:
            data: UV index value (0-11+ scale)

        Returns:
            Encoded bytes representing the UV index (uint8)
        """
        uv_index = int(data)

        # Validate range for uint8 (UV index typically 0-11+, but uint8 allows 0-255)
        if not 0 <= uv_index <= 255:
            raise ValueError(f"UV index {uv_index} is outside valid range (0-255)")

        return bytearray([uv_index])

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "UV Index"
