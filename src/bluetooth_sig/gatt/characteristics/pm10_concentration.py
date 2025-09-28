"""PM10 Concentration characteristic implementation."""

from dataclasses import dataclass

from .templates import ConcentrationCharacteristic


@dataclass
class PM10ConcentrationCharacteristic(ConcentrationCharacteristic):
    """PM10 particulate matter concentration characteristic (0x2BD7).

    Represents particulate matter PM10 concentration in micrograms per
    cubic meter with a resolution of 1 μg/m³.
    """

    _characteristic_name: str = "Particulate Matter - PM10 Concentration"
    _manual_value_type: str = "int"  # Manual override needed as no YAML available

    # Template configuration
    resolution: float = 1.0
    concentration_unit: str = "µg/m³"
    max_value: float = 65533.0  # Exclude special values 0xFFFE and 0xFFFF
