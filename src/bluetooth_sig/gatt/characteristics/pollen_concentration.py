"""Pollen Concentration characteristic implementation."""

from dataclasses import dataclass, field

from ...types.gatt_enums import ValueType
from .templates import Uint24ScaledCharacteristic


@dataclass
class PollenConcentrationCharacteristic(Uint24ScaledCharacteristic):
    """Pollen concentration measurement characteristic (0x2A75).

    Uses uint24 format as per SIG specification.
    Unit: grains/m³ (count per cubic meter)
    """

    _characteristic_name: str = "Pollen Concentration"
    _manual_value_type: ValueType | str | None = "float"  # Override YAML spec since decode_value returns float
    _manual_unit: str | None = field(default="grains/m³", init=False)  # Override template's "units" default

    # SIG specification configuration
    resolution: float = 1.0
