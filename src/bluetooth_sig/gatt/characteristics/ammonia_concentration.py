"""Ammonia Concentration characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import IEEE11073FloatTemplate


class AmmoniaConcentrationCharacteristic(BaseCharacteristic[float]):
    """Ammonia concentration measurement characteristic (0x2BCF).

    Uses IEEE 11073 SFLOAT format (medfloat16) as per SIG specification.
    Unit: kg/m³ (kilogram per cubic meter)
    """

    _manual_unit: str | None = "kg/m³"  # Unit as per SIG specification
    _template = IEEE11073FloatTemplate()
