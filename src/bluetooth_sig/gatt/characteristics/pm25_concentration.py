"""PM2.5 Concentration characteristic implementation."""

from .base import BaseCharacteristic
from .templates import ConcentrationTemplate


class PM25ConcentrationCharacteristic(BaseCharacteristic):
    """PM2.5 particulate matter concentration characteristic (0x2BD6).

    Represents particulate matter PM2.5 concentration in micrograms per
    cubic meter with a resolution of 1 μg/m³.
    """

    _template = ConcentrationTemplate()

    _characteristic_name: str = "Particulate Matter - PM2.5 Concentration"
    resolution: float = 1.0
    _manual_unit: str = "µg/m³"  # Override template's "ppm" default
    max_value: float = 65533.0  # Exclude special values 0xFFFE and 0xFFFF
