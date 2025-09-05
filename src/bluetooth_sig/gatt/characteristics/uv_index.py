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

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "UV Index"
