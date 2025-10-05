"""Pollen Concentration characteristic implementation."""

from ...types.gatt_enums import ValueType
from .base import BaseCharacteristic
from .templates import ScaledUint24Template


class PollenConcentrationCharacteristic(BaseCharacteristic):
    """Pollen concentration measurement characteristic (0x2A75).

    Uses uint24 (3 bytes) format as per SIG specification.
    Unit: grains/m³ (count per cubic meter)
    """

    _template = ScaledUint24Template(scale_factor=1.0)

    _manual_value_type: ValueType | str | None = "float"  # Override YAML spec since decode_value returns float
    _manual_unit: str = "grains/m³"  # Override template's "units" default

    # SIG specification configuration
    resolution: float = 1.0
