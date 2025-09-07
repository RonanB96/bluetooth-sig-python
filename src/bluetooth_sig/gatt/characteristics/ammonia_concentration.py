"""Ammonia Concentration characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class AmmoniaConcentrationCharacteristic(BaseCharacteristic):
    """Ammonia concentration measurement characteristic (0x2BCF).

    Represents ammonia concentration in parts per million (ppm)
    with a resolution of 1 ppm.
    """

    _characteristic_name: str = "Ammonia Concentration"

    def parse_value(self, data: bytearray) -> int:
        """Parse ammonia concentration data (uint16 in units of 1 ppm).

        Args:
            data: Raw BLE characteristic data (2 bytes, little endian)

        Returns:
            Ammonia concentration in parts per million (ppm)

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 2:
            raise ValueError("Ammonia concentration data must be at least 2 bytes")

        # Convert uint16 (little endian) to ammonia concentration in ppm
        concentration_raw = int.from_bytes(data[:2], byteorder="little", signed=False)

        # Handle special values per Bluetooth SIG specification
        if concentration_raw == 0xFFFE:
            raise ValueError("Ammonia concentration is 65534 ppm or greater")
        if concentration_raw == 0xFFFF:
            raise ValueError("Ammonia concentration value is not known")

        return concentration_raw

    def encode_value(self, data: int) -> bytearray:
        """Encode ammonia concentration value back to bytes.

        Args:
            data: Ammonia concentration in ppm

        Returns:
            Encoded bytes representing the ammonia concentration (uint16, 1 ppm resolution)
        """
        concentration = int(data)
        
        # Validate range (realistic ammonia concentration range)
        if not 0 <= concentration <= 65533:  # Exclude special values 0xFFFE and 0xFFFF
            raise ValueError(f"Ammonia concentration {concentration} ppm is outside valid range (0-65533 ppm)")
        
        return bytearray(concentration.to_bytes(2, byteorder="little", signed=False))

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "ppm"
