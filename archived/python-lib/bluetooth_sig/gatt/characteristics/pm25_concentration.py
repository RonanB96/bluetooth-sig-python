"""PM2.5 Concentration characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import IEEE11073FloatTemplate


class PM25ConcentrationCharacteristic(BaseCharacteristic[float]):
    """Particulate Matter - PM2.5 Concentration characteristic (0x2BD6).

    Uses IEEE 11073 SFLOAT format (medfloat16) as per SIG specification.
    Unit: kg/m³ (kilogram per cubic meter)
    """

    _template = IEEE11073FloatTemplate()

    _characteristic_name: str = "Particulate Matter - PM2.5 Concentration"
    _manual_unit: str = "kg/m³"
