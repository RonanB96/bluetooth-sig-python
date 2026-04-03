"""Sulfur Dioxide Concentration characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import IEEE11073FloatTemplate


class SulfurDioxideConcentrationCharacteristic(BaseCharacteristic[float]):
    """Sulfur Dioxide Concentration characteristic (0x2BD8).

    org.bluetooth.characteristic.sulfur_dioxide_concentration

    Represents sulfur dioxide (SO2) concentration using IEEE 11073 SFLOAT
    (medfloat16) format. Unit: kg/m³ per GSS YAML.
    """

    _template = IEEE11073FloatTemplate()

    _manual_unit: str = "kg/m³"
