"""Ozone Concentration characteristic implementation."""

from dataclasses import dataclass, field

from ...types.gatt_enums import ValueType
from .templates import ConcentrationCharacteristic


@dataclass
class OzoneConcentrationCharacteristic(ConcentrationCharacteristic):
    """Ozone concentration measurement characteristic (0x2BD4).

    Represents ozone concentration in parts per billion (ppb) with a
    resolution of 1 ppb.
    """

    _characteristic_name: str = "Ozone Concentration"
    _manual_value_type: ValueType | str | None = ValueType.INT  # Manual override needed as no YAML available
    _manual_unit: str | None = field(default="ppb", init=False)  # Override template's "ppm" default

    # Template configuration
    resolution: float = 1.0
    max_value: float = 65533.0  # Exclude special values 0xFFFE and 0xFFFF
