# pylint: disable=duplicate-code  # Concentration characteristics share template configuration
"""Ozone Concentration characteristic implementation."""

from __future__ import annotations

from ...types.gatt_enums import ValueType
from .base import BaseCharacteristic
from .templates import ConcentrationTemplate


class OzoneConcentrationCharacteristic(BaseCharacteristic[float]):
    """Ozone concentration measurement characteristic (0x2BD4).

    Represents ozone concentration in parts per billion (ppb) with a
    resolution of 1 ppb.
    """

    _template = ConcentrationTemplate()

    _manual_value_type: ValueType | str | None = ValueType.INT  # Manual override needed as no YAML available
    _manual_unit: str = "ppb"  # Override template's "ppm" default

    # Template configuration
    resolution: float = 1.0
