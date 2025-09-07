"""Electric Current Statistics characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class ElectricCurrentStatisticsCharacteristic(BaseCharacteristic):
    """Electric Current Statistics characteristic.

    Provides statistical current data (min, max, average over time).
    """

    _characteristic_name: str = "Electric Current Statistics"
    _manual_value_type: str = (
        "dict"  # Override YAML int type since parse_value returns dict
    )

    def parse_value(self, data: bytearray) -> dict[str, float]:
        """Parse current statistics data (3x uint16 in units of 0.01 A).

        Args:
            data: Raw bytes from the characteristic read

        Returns:
            Dictionary with 'minimum', 'maximum', and 'average' current values in Amperes

        Raises:
            ValueError: If data is insufficient
        """
        if len(data) < 6:
            raise ValueError(
                "Electric current statistics data must be at least 6 bytes"
            )

        # Convert 3x uint16 (little endian) to current statistics in Amperes
        min_current_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        max_current_raw = int.from_bytes(data[2:4], byteorder="little", signed=False)
        avg_current_raw = int.from_bytes(data[4:6], byteorder="little", signed=False)

        return {
            "minimum": min_current_raw * 0.01,
            "maximum": max_current_raw * 0.01,
            "average": avg_current_raw * 0.01,
        }

    def encode_value(self, data) -> bytearray:
        """Encode value back to bytes - basic stub implementation."""
        # TODO: Implement proper encoding
        raise NotImplementedError(
            "encode_value not yet implemented for this characteristic"
        )

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "A"
