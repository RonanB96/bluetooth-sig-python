"""Supported Power Range characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class SupportedPowerRangeCharacteristic(BaseCharacteristic):
    """Supported Power Range characteristic.

    Specifies minimum and maximum power values for power capability specification.
    """

    _characteristic_name: str = "Supported Power Range"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "dict"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> dict[str, int]:
        """Parse supported power range data (2x sint16 in watts).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            Dictionary with 'minimum' and 'maximum' power values in Watts

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 4:
            raise ValueError("Supported power range data must be at least 4 bytes")

        # Convert 2x sint16 (little endian) to power range in Watts
        min_power_raw = int.from_bytes(data[:2], byteorder="little", signed=True)
        max_power_raw = int.from_bytes(data[2:4], byteorder="little", signed=True)

        return {"minimum": min_power_raw, "maximum": max_power_raw}

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "W"

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "power"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return ""  # Range specification doesn't have a standard state class
