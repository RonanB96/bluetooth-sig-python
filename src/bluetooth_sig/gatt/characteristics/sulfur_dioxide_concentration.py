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

    def encode_value(self, data: int) -> bytearray:
        """Encode sulfur dioxide concentration value back to bytes.

        Args:
            data: Sulfur dioxide concentration in ppb

        Returns:
            Encoded bytes representing the sulfur dioxide concentration (uint16, 1 ppb resolution)
        """
        concentration = int(data)

        # Validate range (realistic sulfur dioxide concentration range)
        if not 0 <= concentration <= 65533:  # Exclude special values 0xFFFE and 0xFFFF
            raise ValueError(
                f"Sulfur dioxide concentration {concentration} ppb is outside valid range (0-65533 ppb)"
            )

        return bytearray(concentration.to_bytes(2, byteorder="little", signed=False))

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "ppb"
