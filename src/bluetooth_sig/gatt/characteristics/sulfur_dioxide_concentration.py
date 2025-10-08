"""Sulfur Dioxide Concentration characteristic implementation."""

from __future__ import annotations

from ...types.gatt_enums import ValueType
from .base import BaseCharacteristic
from .templates import ConcentrationTemplate


class SulfurDioxideConcentrationCharacteristic(BaseCharacteristic):
    """Sulfur dioxide concentration measurement characteristic (0x2BD3).

    Represents sulfur dioxide (SO2) concentration in parts per billion
    (ppb) with a resolution of 1 ppb.
    """

    _template = ConcentrationTemplate()

    _manual_value_type: ValueType | str | None = ValueType.INT
    _manual_unit: str = "ppb"  # Override template's "ppm" default

    # Template configuration
    resolution: float = 1.0
    max_value: float = 65533.0  # Exclude special values 0xFFFE and 0xFFFF
