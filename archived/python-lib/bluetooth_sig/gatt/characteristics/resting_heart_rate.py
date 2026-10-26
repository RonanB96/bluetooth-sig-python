"""Resting Heart Rate characteristic (0x2A92)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class RestingHeartRateCharacteristic(BaseCharacteristic[int]):
    """Resting Heart Rate characteristic (0x2A92).

    org.bluetooth.characteristic.resting_heart_rate

    Resting Heart Rate characteristic.
    """

    _template = Uint8Template()
