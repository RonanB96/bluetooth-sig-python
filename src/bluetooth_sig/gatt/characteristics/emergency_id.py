"""Emergency ID characteristic (0x2B2D)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class EmergencyIdCharacteristic(BaseCharacteristic[str]):
    """Emergency ID characteristic (0x2B2D).

    org.bluetooth.characteristic.emergency_id

    Emergency ID characteristic.
    """

    _template = Utf8StringTemplate()
    min_length = 0
