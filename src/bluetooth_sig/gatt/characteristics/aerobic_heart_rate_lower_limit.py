"""Aerobic Heart Rate Lower Limit characteristic (0x2A7E)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class AerobicHeartRateLowerLimitCharacteristic(BaseCharacteristic):
    """Aerobic Heart Rate Lower Limit characteristic (0x2A7E).

    org.bluetooth.characteristic.aerobic_heart_rate_lower_limit

    Aerobic Heart Rate Lower Limit characteristic.
    """

    _template = Uint8Template()
