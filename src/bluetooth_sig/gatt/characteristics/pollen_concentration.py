"""Pollen Concentration characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class PollenConcentrationCharacteristic(BaseCharacteristic):
    """Pollen concentration characteristic.

    Represents the pollen count in count per cubic meter.
    """

    _characteristic_name: str = "Pollen Concentration"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "int"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> int:
        """Parse pollen concentration data (uint24 in count per cubic meter)."""
        if len(data) < 3:
            raise ValueError("Pollen concentration data must be at least 3 bytes")

        # Parse uint24 (little endian) - pad to 4 bytes for parsing
        raw_bytes = data[:3] + b"\x00"  # Pad to 4 bytes
        concentration = int.from_bytes(raw_bytes, byteorder="little", signed=False)

        return concentration

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "count/m³"

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "aqi"  # Air quality index is closest match

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "measurement"
