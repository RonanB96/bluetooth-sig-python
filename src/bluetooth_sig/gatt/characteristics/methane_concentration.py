"""Methane Concentration characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class MethaneConcentrationCharacteristic(BaseCharacteristic):
    """Methane concentration measurement characteristic (0x2BD1).

    Represents methane concentration in parts per million (ppm)
    with a resolution of 1 ppm.
    """

    _characteristic_name: str = "Methane Concentration"
    _manual_value_type: str = "int"  # Manual override needed as no YAML available

    def decode_value(self, data: bytearray) -> int:
        """Parse methane concentration data (uint16 in units of 1 ppm).

        Args:
            data: Raw BLE characteristic data (2 bytes, little endian)

        Returns:
            Methane concentration in parts per million (ppm)

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 2:
            raise ValueError("Methane concentration data must be at least 2 bytes")

        # Convert uint16 (little endian) to methane concentration in ppm
        concentration_raw = int.from_bytes(data[:2], byteorder="little", signed=False)

        # Handle special values per Bluetooth SIG specification
        if concentration_raw == 0xFFFE:
            raise ValueError("Methane concentration is 65534 ppm or greater")
        if concentration_raw == 0xFFFF:
            raise ValueError("Methane concentration value is not known")

        return concentration_raw

    def encode_value(self, data: int) -> bytearray:
        """Encode methane concentration value back to bytes.

        Args:
            data: Methane concentration in ppm

        Returns:
            Encoded bytes representing the methane concentration (uint16, 1 ppm resolution)
        """
        concentration = int(data)

        # Validate range (realistic methane concentration range)
        if not 0 <= concentration <= 65533:  # Exclude special values 0xFFFE and 0xFFFF
            raise ValueError(
                f"Methane concentration {concentration} ppm is outside valid range (0-65533 ppm)"
            )

        return bytearray(concentration.to_bytes(2, byteorder="little", signed=False))

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "ppm"
