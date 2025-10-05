"""CO2 Concentration characteristic implementation."""

from ...types.gatt_enums import ValueType
from .base import BaseCharacteristic
from .templates import ConcentrationTemplate


class CO2ConcentrationCharacteristic(BaseCharacteristic):
    """CO2 concentration measurement characteristic (0x2B8C).

    Represents carbon dioxide concentration in parts per million (ppm)
    with a resolution of 1 ppm.
    """

    _template = ConcentrationTemplate()

    _characteristic_name: str = "CO\\textsubscript{2} Concentration"
    _manual_value_type: ValueType | str | None = ValueType.INT
    _manual_unit: str = "ppm"  # Override template's "ppm" default

    # Template configuration
    resolution: float = 1.0
    max_value: float = 65533.0  # Exclude special values 0xFFFE and 0xFFFF
