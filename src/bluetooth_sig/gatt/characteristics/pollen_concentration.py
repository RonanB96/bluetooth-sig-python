"""Pollen Concentration characteristic implementation."""

from dataclasses import dataclass

from .templates import ConcentrationCharacteristic


@dataclass
class PollenConcentrationCharacteristic(ConcentrationCharacteristic):
    """Pollen concentration measurement characteristic (0x2A75).

    Represents pollen concentration in grains per cubic meter
    with a resolution of 1 grains/m³.
    """

    _characteristic_name: str = "Pollen Concentration"
    
    # Template configuration
    resolution: float = 1.0
    concentration_unit: str = "grains/m³"
    max_value: float = 65533.0  # Exclude special values 0xFFFE and 0xFFFF