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

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "int"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> int:
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

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "ppm"

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return "gas"

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "measurement"
