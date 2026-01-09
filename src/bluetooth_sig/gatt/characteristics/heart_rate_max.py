"""Heart Rate Max characteristic (0x2A8D)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class HeartRateMaxCharacteristic(BaseCharacteristic[int]):
    """Heart Rate Max characteristic (0x2A8D).

    org.bluetooth.characteristic.heart_rate_max

    Heart Rate Max characteristic.
    """

    _template = Uint8Template()
