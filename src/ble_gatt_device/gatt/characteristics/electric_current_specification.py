"""Electric Current Specification characteristic implementation."""

from dataclasses import dataclass
from typing import Dict

from .base import BaseCharacteristic


@dataclass
class ElectricCurrentSpecificationCharacteristic(BaseCharacteristic):
    """Electric Current Specification characteristic.

    Specifies minimum and maximum current values for electrical specifications.
    """

    _characteristic_name: str = "Electric Current Specification"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "dict"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> Dict[str, float]:
        """Parse current specification data (2x uint16 in units of 0.01 A).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            Dictionary with 'minimum' and 'maximum' current specification values in Amperes

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 4:
            raise ValueError(
                "Electric current specification data must be at least 4 bytes"
            )

        # Convert 2x uint16 (little endian) to current specification in Amperes
        min_current_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        max_current_raw = int.from_bytes(data[2:4], byteorder="little", signed=False)

        return {"minimum": min_current_raw * 0.01, "maximum": max_current_raw * 0.01}

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "A"

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "current"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return ""  # Specification data doesn't have a standard state class
