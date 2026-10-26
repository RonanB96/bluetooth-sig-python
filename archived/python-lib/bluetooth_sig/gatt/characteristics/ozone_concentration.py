# pylint: disable=duplicate-code  # Concentration characteristics share template configuration
"""Ozone Concentration characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import IEEE11073FloatTemplate


class OzoneConcentrationCharacteristic(BaseCharacteristic[float]):
    """Ozone concentration measurement characteristic (0x2BD4).

    Represents ozone concentration using IEEE 11073 SFLOAT (medfloat16) format.
    Unit: kg/m³ per GSS YAML.
    """

    _template = IEEE11073FloatTemplate()

    _manual_unit: str = "kg/m³"
