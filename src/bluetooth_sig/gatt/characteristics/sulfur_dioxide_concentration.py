"""Sulfur Dioxide Concentration characteristic implementation."""

from dataclasses import dataclass

from .templates import ConcentrationCharacteristic


@dataclass
class SulfurDioxideConcentrationCharacteristic(ConcentrationCharacteristic):
    """Sulfur dioxide concentration measurement characteristic (0x2BD8).

    Represents sulfur dioxide (SO2) concentration in parts per billion (ppb)
    with a resolution of 1 ppb.
    """

    _characteristic_name: str = "Sulfur Dioxide Concentration"
    _manual_value_type: str = "int"  # Manual override needed as no YAML available
    
    # Template configuration
    resolution: float = 1.0
    concentration_unit: str = "ppb"
    max_value: float = 65533.0  # Exclude special values 0xFFFE and 0xFFFF
