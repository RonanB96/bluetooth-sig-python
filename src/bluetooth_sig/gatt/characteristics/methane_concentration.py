"""Methane Concentration characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import IEEE11073FloatTemplate


class MethaneConcentrationCharacteristic(BaseCharacteristic[float]):
    """Methane concentration measurement characteristic (0x2BD1).

    Represents methane concentration using IEEE 11073 SFLOAT (medfloat16) format.
    Unit: parts per billion (ppb) per GSS YAML.
    """

    _template = IEEE11073FloatTemplate()

    _manual_unit: str = "ppb"
