"""Apparent Wind Speed characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class ApparentWindSpeedCharacteristic(BaseCharacteristic[float]):
    """Apparent Wind Speed characteristic (0x2A72).

    org.bluetooth.characteristic.apparent_wind_speed

    Apparent Wind Speed measurement characteristic.
    """

    _template = ScaledUint16Template.from_letter_method(M=1, d=-2, b=0)
