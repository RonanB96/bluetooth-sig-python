"""Nitrogen Dioxide Concentration characteristic implementation."""

from dataclasses import dataclass, field

from .templates import ConcentrationCharacteristic


@dataclass
class NitrogenDioxideConcentrationCharacteristic(ConcentrationCharacteristic):
    """Nitrogen dioxide concentration measurement characteristic (0x2BD2).

    Represents nitrogen dioxide (NO2) concentration in parts per billion
    (ppb) with a resolution of 1 ppb.
    """

    _characteristic_name: str = "Nitrogen Dioxide Concentration"
    _manual_unit: str | None = field(default="ppb", init=False)  # Override template's "ppm" default

    # Template configuration
    resolution: float = 1.0
    max_value: float = 65533.0  # Exclude special values 0xFFFE and 0xFFFF
