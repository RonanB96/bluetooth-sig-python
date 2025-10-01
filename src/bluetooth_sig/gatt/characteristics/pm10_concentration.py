"""PM10 Concentration characteristic implementation."""

from dataclasses import dataclass, field

from ...types.gatt_enums import ValueType
from .templates import ConcentrationCharacteristic


@dataclass
class PM10ConcentrationCharacteristic(ConcentrationCharacteristic):
    """PM10 particulate matter concentration characteristic (0x2BD7).

    Represents particulate matter PM10 concentration in micrograms per
    cubic meter with a resolution of 1 μg/m³.
    """

    _characteristic_name: str = "Particulate Matter - PM10 Concentration"
    _manual_value_type: ValueType | str | None = ValueType.INT
    _manual_unit: str | None = field(default="µg/m³", init=False)  # Override template's "ppm" default

    # Template configuration
    resolution: float = 1.0
    max_value: float = 65533.0  # Exclude special values 0xFFFE and 0xFFFF
