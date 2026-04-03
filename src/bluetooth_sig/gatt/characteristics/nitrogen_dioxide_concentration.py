"""Nitrogen Dioxide Concentration characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import IEEE11073FloatTemplate


class NitrogenDioxideConcentrationCharacteristic(BaseCharacteristic[float]):
    """Nitrogen dioxide concentration measurement characteristic (0x2BD2).

    Represents nitrogen dioxide (NO2) concentration using IEEE 11073 SFLOAT
    (medfloat16) format. Unit: kg/m³ per GSS YAML.
    """

    _template = IEEE11073FloatTemplate()

    _manual_unit: str = "kg/m³"
