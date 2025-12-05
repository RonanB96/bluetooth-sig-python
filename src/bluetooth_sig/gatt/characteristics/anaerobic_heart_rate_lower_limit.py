"""Anaerobic Heart Rate Lower Limit characteristic (0x2A81)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class AnaerobicHeartRateLowerLimitCharacteristic(BaseCharacteristic):
    """Anaerobic Heart Rate Lower Limit characteristic (0x2A81).

    org.bluetooth.characteristic.anaerobic_heart_rate_lower_limit

    Anaerobic Heart Rate Lower Limit characteristic.
    """

    _template = Uint8Template()
