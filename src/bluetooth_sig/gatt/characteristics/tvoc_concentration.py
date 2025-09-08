"""TVOC Concentration characteristic implementation."""

from dataclasses import dataclass

from .templates import ConcentrationCharacteristic


@dataclass
class TVOCConcentrationCharacteristic(ConcentrationCharacteristic):
    """Total Volatile Organic Compounds concentration characteristic (0x2BE8).

    Represents TVOC concentration in parts per billion (ppb)
    with a resolution of 1 ppb.
    """

    _characteristic_name: str = "Total Volatile Organic Compounds Concentration"
    _manual_value_type: str = "int"  # Manual override needed as no YAML available
    
    # Template configuration
    resolution: float = 1.0
    concentration_unit: str = "ppb"
    max_value: float = 65533.0  # Exclude special values 0xFFFE and 0xFFFF