"""Nitrogen Dioxide Concentration characteristic implementation."""

from .base import BaseCharacteristic
from .templates import ConcentrationTemplate


class NitrogenDioxideConcentrationCharacteristic(BaseCharacteristic):
    """Nitrogen dioxide concentration measurement characteristic (0x2BD2).

    Represents nitrogen dioxide (NO2) concentration in parts per billion
    (ppb) with a resolution of 1 ppb.
    """

    _template = ConcentrationTemplate()

    _characteristic_name: str = "Nitrogen Dioxide Concentration"
    _manual_unit: str = "ppb"  # Override template's "ppm" default

    # Template configuration
    resolution: float = 1.0
    max_value: float = 65533.0  # Exclude special values 0xFFFE and 0xFFFF
