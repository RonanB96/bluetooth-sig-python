"""True Wind Speed characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class TrueWindSpeedCharacteristic(BaseCharacteristic):
    """True Wind Speed characteristic (0x2A70).

    org.bluetooth.characteristic.true_wind_speed

    True Wind Speed measurement characteristic.
    """

    _template = ScaledUint16Template.from_letter_method(M=1, d=-2, b=0)
