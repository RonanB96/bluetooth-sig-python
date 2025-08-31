"""Air quality sensor characteristic implementations."""

from dataclasses import dataclass

from ..base import BaseCharacteristic


@dataclass
class CarbonMonoxideConcentrationCharacteristic(BaseCharacteristic):
    """Carbon Monoxide Concentration characteristic (UUID: 0x2BD6).
    
    Measures CO concentration in mg/m³ according to Bluetooth SIG specification.
    Data format: uint16 representing concentration in 0.01 mg/m³ resolution.
    """

    _characteristic_name: str = "Carbon Monoxide Concentration"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse CO concentration data (uint16 in units of 0.01 mg/m³).
        
        Args:
            data: Raw byte data from BLE characteristic
            
        Returns:
            CO concentration in mg/m³
            
        Raises:
            ValueError: If data is insufficient or malformed
        """
        if len(data) < 2:
            raise ValueError("CO concentration data must be at least 2 bytes")

        # Convert uint16 (little endian) to concentration in mg/m³
        concentration_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return concentration_raw * 0.01

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "mg/m³"


@dataclass
class PM25ConcentrationCharacteristic(BaseCharacteristic):
    """PM2.5 Particulate Matter Concentration characteristic (UUID: 0x2BD1).
    
    Measures PM2.5 concentration in μg/m³ according to Bluetooth SIG specification.
    Data format: uint16 representing concentration in 1 μg/m³ resolution.
    """

    _characteristic_name: str = "PM2.5 Concentration"

    def __post_init__(self):
        """Initialize with specific value type and unit."""
        self.value_type = "float"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> float:
        """Parse PM2.5 concentration data (uint16 in units of 1 μg/m³).
        
        Args:
            data: Raw byte data from BLE characteristic
            
        Returns:
            PM2.5 concentration in μg/m³
            
        Raises:
            ValueError: If data is insufficient or malformed
        """
        if len(data) < 2:
            raise ValueError("PM2.5 concentration data must be at least 2 bytes")

        # Convert uint16 (little endian) to concentration in μg/m³
        concentration_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return float(concentration_raw)

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "μg/m³"