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

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "int"
        super().__post_init__()

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

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "ppm"
