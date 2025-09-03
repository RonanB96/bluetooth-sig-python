"""Electric Current Range characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class ElectricCurrentRangeCharacteristic(BaseCharacteristic):
    """Electric Current Range characteristic.

    Specifies lower and upper current bounds (2x uint16).
    """

    _characteristic_name: str = "Electric Current Range"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "dict"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> dict[str, float]:
        """Parse current range data (2x uint16 in units of 0.01 A).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            Dictionary with 'min' and 'max' current values in Amperes

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 4:
            raise ValueError("Electric current range data must be at least 4 bytes")

        # Convert 2x uint16 (little endian) to current range in Amperes
        min_current_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        max_current_raw = int.from_bytes(data[2:4], byteorder="little", signed=False)

        return {"min": min_current_raw * 0.01, "max": max_current_raw * 0.01}

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "A"
