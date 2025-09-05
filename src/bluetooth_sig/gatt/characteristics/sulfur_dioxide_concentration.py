"""Sulfur Dioxide Concentration characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class SulfurDioxideConcentrationCharacteristic(BaseCharacteristic):
    """Sulfur dioxide concentration measurement characteristic (0x2BD8).

    Represents sulfur dioxide (SO2) concentration in parts per billion (ppb)
    with a resolution of 1 ppb.
    """

    _characteristic_name: str = "Sulfur Dioxide Concentration"
    _manual_value_type: str = "int"  # Manual override needed as no YAML available

    def parse_value(self, data: bytearray) -> int:
        """Parse sulfur dioxide concentration data (uint16 in units of 1 ppb).

        Args:
            data: Raw BLE characteristic data (2 bytes, little endian)

        Returns:
            Sulfur dioxide concentration in parts per billion (ppb)

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 2:
            raise ValueError(
                "Sulfur dioxide concentration data must be at least 2 bytes"
            )

        # Convert uint16 (little endian) to SO2 concentration in ppb
        concentration_raw = int.from_bytes(data[:2], byteorder="little", signed=False)

        # Handle special values per Bluetooth SIG specification
        if concentration_raw == 0xFFFE:
            raise ValueError("Sulfur dioxide concentration is 65534 ppb or greater")
        if concentration_raw == 0xFFFF:
            raise ValueError("Sulfur dioxide concentration value is not known")

        return concentration_raw

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "ppb"
