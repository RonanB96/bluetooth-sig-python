"""Dew Point characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledSint8Template


class DewPointCharacteristic(BaseCharacteristic[float]):
    """Dew Point characteristic (0x2A7B).

    org.bluetooth.characteristic.dew_point

    Dew Point measurement characteristic.
    """

    _template = ScaledSint8Template.from_letter_method(M=1, d=0, b=0)
