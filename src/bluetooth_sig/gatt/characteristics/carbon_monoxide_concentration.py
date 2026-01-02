"""Carbon Monoxide Concentration characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import IEEE11073FloatTemplate


class CarbonMonoxideConcentrationCharacteristic(BaseCharacteristic):
    """Carbon Monoxide Concentration characteristic (0x2BD0).

    org.bluetooth.characteristic.carbon_monoxide_concentration

    Represents carbon monoxide concentration measurement using IEEE 11073 SFLOAT format.
    """

    _template = IEEE11073FloatTemplate()
