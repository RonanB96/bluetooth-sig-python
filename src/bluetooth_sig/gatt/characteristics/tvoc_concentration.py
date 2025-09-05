"""TVOC Concentration characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class TVOCConcentrationCharacteristic(BaseCharacteristic):
    """TVOC (Total Volatile Organic Compounds) concentration characteristic (0x2BE7).

    Represents volatile organic compounds concentration in parts per billion (ppb)
    with a resolution of 1 ppb.
    """

    _characteristic_name: str = "VOC Concentration"

    def parse_value(self, data: bytearray) -> int:
        """Parse TVOC concentration data (uint16 in units of 1 ppb).

        Args:
            data: Raw BLE characteristic data (2 bytes, little endian)

        Returns:
            TVOC concentration in parts per billion (ppb)

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 2:
            raise ValueError("TVOC concentration data must be at least 2 bytes")

        # Convert uint16 (little endian) to TVOC concentration in ppb
        concentration_raw = int.from_bytes(data[:2], byteorder="little", signed=False)

        # Handle special values per Bluetooth SIG specification
        if concentration_raw == 0xFFFE:
            raise ValueError("TVOC concentration is 65534 ppb or greater")
        if concentration_raw == 0xFFFF:
            raise ValueError("TVOC concentration value is not known")

        return concentration_raw

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "ppb"
