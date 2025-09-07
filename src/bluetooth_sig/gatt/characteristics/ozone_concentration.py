"""Ozone Concentration characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class OzoneConcentrationCharacteristic(BaseCharacteristic):
    """Ozone concentration measurement characteristic (0x2BD4).

    Represents ozone concentration in parts per billion (ppb)
    with a resolution of 1 ppb.
    """

    _characteristic_name: str = "Ozone Concentration"
    _manual_value_type: str = "int"  # Manual override needed as no YAML available

    def parse_value(self, data: bytearray) -> int:
        """Parse ozone concentration data (uint16 in units of 1 ppb).

        Args:
            data: Raw BLE characteristic data (2 bytes, little endian)

        Returns:
            Ozone concentration in parts per billion (ppb)

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 2:
            raise ValueError("Ozone concentration data must be at least 2 bytes")

        # Convert uint16 (little endian) to ozone concentration in ppb
        concentration_raw = int.from_bytes(data[:2], byteorder="little", signed=False)

        # Handle special values per Bluetooth SIG specification
        if concentration_raw == 0xFFFE:
            raise ValueError("Ozone concentration is 65534 ppb or greater")
        if concentration_raw == 0xFFFF:
            raise ValueError("Ozone concentration value is not known")

        return concentration_raw

    def encode_value(self, data: int) -> bytearray:
        """Encode ozone concentration value back to bytes.

        Args:
            data: Ozone concentration in ppb

        Returns:
            Encoded bytes representing the ozone concentration (uint16, 1 ppb resolution)
        """
        concentration = int(data)

        # Validate range (realistic ozone concentration range)
        if not 0 <= concentration <= 65533:  # Exclude special values 0xFFFE and 0xFFFF
            raise ValueError(
                f"Ozone concentration {concentration} ppb is outside valid range (0-65533 ppb)"
            )

        return bytearray(concentration.to_bytes(2, byteorder="little", signed=False))

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "ppb"
