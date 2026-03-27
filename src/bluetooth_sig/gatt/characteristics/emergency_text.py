"""Emergency Text characteristic (0x2B2E)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class EmergencyTextCharacteristic(BaseCharacteristic[str]):
    """Emergency Text characteristic (0x2B2E).

    org.bluetooth.characteristic.emergency_text

    Emergency Text characteristic.
    """

    _template = Utf8StringTemplate()
    min_length = 0
