"""PM10 Concentration characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class PM10ConcentrationCharacteristic(BaseCharacteristic):
    """PM10 particulate matter concentration characteristic (0x2BD7).

    Represents particulate matter PM10 concentration in micrograms per cubic meter
    with a resolution of 1 μg/m³.
    """

    _characteristic_name: str = "Particulate Matter - PM10 Concentration"
    _manual_value_type: str = "int"  # Manual override needed as no YAML available

    def parse_value(self, data: bytearray) -> int:
        """Parse PM10 concentration data (uint16 in units of 1 μg/m³).

        Args:
            data: Raw BLE characteristic data (2 bytes, little endian)

        Returns:
            PM10 concentration in micrograms per cubic meter (μg/m³)

        Raises:
            ValueError: If data format is invalid
        """
        if len(data) < 2:
            raise ValueError("PM10 concentration data must be at least 2 bytes")

        # Convert uint16 (little endian) to PM10 concentration in μg/m³
        concentration_raw = int.from_bytes(data[:2], byteorder="little", signed=False)

        # Handle special values per Bluetooth SIG specification
        if concentration_raw == 0xFFFE:
            raise ValueError("PM10 concentration is 65534 μg/m³ or greater")
        if concentration_raw == 0xFFFF:
            raise ValueError("PM10 concentration value is not known")

        return concentration_raw

    def encode_value(self, data: int) -> bytearray:
        """Encode PM10 concentration value back to bytes.

        Args:
            data: PM10 concentration in μg/m³

        Returns:
            Encoded bytes representing the PM10 concentration (uint16, 1 μg/m³ resolution)
        """
        concentration = int(data)
        
        # Validate range (realistic PM10 concentration range)
        if not 0 <= concentration <= 65533:  # Exclude special values 0xFFFE and 0xFFFF
            raise ValueError(f"PM10 concentration {concentration} μg/m³ is outside valid range (0-65533 μg/m³)")
        
        return bytearray(concentration.to_bytes(2, byteorder="little", signed=False))

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "µg/m³"
