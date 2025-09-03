"""UV Index characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class UVIndexCharacteristic(BaseCharacteristic):
    """UV Index characteristic."""

    _characteristic_name: str = "UV Index"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse UV Index data (uint8)."""
        if len(data) < 1:
            raise ValueError("UV Index data must be at least 1 byte")

        # UV Index is a uint8 value
        return float(data[0])

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "UV Index"
