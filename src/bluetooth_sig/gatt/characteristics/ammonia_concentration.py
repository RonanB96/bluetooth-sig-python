"""Ammonia Concentration characteristic implementation."""

from dataclasses import dataclass

from .templates import ConcentrationCharacteristic


@dataclass
class AmmoniaConcentrationCharacteristic(ConcentrationCharacteristic):
    """Ammonia concentration measurement characteristic (0x2BCF).

    Represents ammonia concentration in parts per million (ppm)
    with a resolution of 1 ppm.
    """

    _characteristic_name: str = "Ammonia Concentration"

    # Template configuration
    resolution: float = 1.0
    concentration_unit: str = "ppm"
    max_value: float = 65533.0  # Exclude special values 0xFFFE and 0xFFFF
