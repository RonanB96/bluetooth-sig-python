"""True Wind Direction characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class TrueWindDirectionCharacteristic(BaseCharacteristic):
    """True Wind Direction characteristic (0x2A71).

    org.bluetooth.characteristic.true_wind_direction

    True Wind Direction measurement characteristic.
    """

    _template = ScaledUint16Template.from_letter_method(M=1, d=-2, b=0)
