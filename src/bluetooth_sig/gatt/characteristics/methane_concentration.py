"""Methane Concentration characteristic implementation."""

from dataclasses import dataclass

from .templates import ConcentrationCharacteristic


@dataclass
class MethaneConcentrationCharacteristic(ConcentrationCharacteristic):
    """Methane concentration measurement characteristic (0x2BD1).

    Represents methane concentration in parts per million (ppm)
    with a resolution of 1 ppm.
    """

    _characteristic_name: str = "Methane Concentration"
    _manual_value_type: str = "int"  # Manual override needed as no YAML available

    # Template configuration
    resolution: float = 1.0
    concentration_unit: str = "ppm"
    max_value: float = 65533.0  # Exclude special values 0xFFFE and 0xFFFF
