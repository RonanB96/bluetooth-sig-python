"""PM2.5 Concentration characteristic implementation."""

from dataclasses import dataclass

from .templates import ConcentrationCharacteristic


@dataclass
class PM25ConcentrationCharacteristic(ConcentrationCharacteristic):
    """PM2.5 particulate matter concentration characteristic (0x2BD6).

    Represents particulate matter PM2.5 concentration in micrograms per cubic meter
    with a resolution of 1 μg/m³.
    """

    _characteristic_name: str = "Particulate Matter - PM2.5 Concentration"

    # Template configuration
    resolution: float = 1.0
    concentration_unit: str = "µg/m³"
    max_value: float = 65533.0  # Exclude special values 0xFFFE and 0xFFFF
