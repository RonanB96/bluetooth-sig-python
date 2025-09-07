"""CO2 Concentration characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class CO2ConcentrationCharacteristic(BaseCharacteristic):
    """CO2 concentration measurement characteristic (0x2B8C).

    Represents carbon dioxide concentration in parts per million (ppm)
    with a resolution of 1 ppm.
    """

    _characteristic_name: str = "CO\\textsubscript{2} Concentration"

    def parse_value(self, data: bytearray) -> int:
        """Parse CO2 concentration data (uint16 in units of 1 ppm).

        Args:
            data: Raw BLE characteristic data (2 bytes, little endian)

        Returns:
            CO2 concentration in parts per million (ppm)

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 2:
            raise ValueError("CO2 concentration data must be at least 2 bytes")

        # Convert uint16 (little endian) to CO2 concentration in ppm
        concentration_raw = int.from_bytes(data[:2], byteorder="little", signed=False)

        # Handle special values per Bluetooth SIG specification
        if concentration_raw == 0xFFFE:
            raise ValueError("CO2 concentration is 65534 ppm or greater")
        if concentration_raw == 0xFFFF:
            raise ValueError("CO2 concentration value is not known")

        return concentration_raw

    def encode_value(self, data: int) -> bytearray:
        """Encode CO2 concentration value back to bytes.

        Args:
            data: CO2 concentration in ppm

        Returns:
            Encoded bytes representing the CO2 concentration (uint16, 1 ppm resolution)
        """
        concentration = int(data)
        
        # Validate range (realistic CO2 concentration range)
        if not 0 <= concentration <= 65533:  # Exclude special values 0xFFFE and 0xFFFF
            raise ValueError(f"CO2 concentration {concentration} ppm is outside valid range (0-65533 ppm)")
        
        return bytearray(concentration.to_bytes(2, byteorder="little", signed=False))

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "ppm"
