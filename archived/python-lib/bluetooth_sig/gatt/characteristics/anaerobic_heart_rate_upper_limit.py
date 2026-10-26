"""Anaerobic Heart Rate Upper Limit characteristic (0x2A82)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class AnaerobicHeartRateUpperLimitCharacteristic(BaseCharacteristic[int]):
    """Anaerobic Heart Rate Upper Limit characteristic (0x2A82).

    org.bluetooth.characteristic.anaerobic_heart_rate_upper_limit

    Anaerobic Heart Rate Upper Limit characteristic.
    """

    _template = Uint8Template()
