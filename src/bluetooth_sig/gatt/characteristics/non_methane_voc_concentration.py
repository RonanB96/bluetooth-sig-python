"""Non-Methane Volatile Organic Compounds Concentration characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import IEEE11073FloatTemplate


class NonMethaneVOCConcentrationCharacteristic(BaseCharacteristic):
    """Non-Methane Volatile Organic Compounds concentration characteristic (0x2BD3).

    Uses IEEE 11073 SFLOAT format (medfloat16) as per SIG specification.
    Unit: kg/m³ (kilogram per cubic meter)
    """

    _template = IEEE11073FloatTemplate()

    _characteristic_name: str = "Non-Methane Volatile Organic Compounds Concentration"
    _manual_unit: str = "kg/m³"  # Unit as per SIG specification
