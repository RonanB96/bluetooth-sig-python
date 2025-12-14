"""Apparent Wind Direction characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class ApparentWindDirectionCharacteristic(BaseCharacteristic):
    """Apparent Wind Direction characteristic (0x2A73).

    org.bluetooth.characteristic.apparent_wind_direction

    Apparent Wind Direction measurement characteristic.
    """

    _template = ScaledUint16Template.from_letter_method(M=1, d=-2, b=0)

    expected_length: int = 2
    expected_type: type = float
