"""Electric Current Specification characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class ElectricCurrentSpecificationCharacteristic(BaseCharacteristic):
    """Electric Current Specification characteristic.

    Specifies minimum and maximum current values for electrical specifications.
    """

    _characteristic_name: str = "Electric Current Specification"

    def parse_value(self, data: bytearray) -> dict[str, float]:
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


    def encode_value(self, data) -> bytearray:
        """Encode value back to bytes - basic stub implementation."""
        # TODO: Implement proper encoding
        raise NotImplementedError("encode_value not yet implemented for this characteristic")
    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "A"
