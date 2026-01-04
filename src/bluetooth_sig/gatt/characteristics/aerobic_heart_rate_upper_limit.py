"""Aerobic Heart Rate Upper Limit characteristic (0x2A84)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class AerobicHeartRateUpperLimitCharacteristic(BaseCharacteristic[int]):
    """Aerobic Heart Rate Upper Limit characteristic (0x2A84).

    org.bluetooth.characteristic.aerobic_heart_rate_upper_limit

    Aerobic Heart Rate Upper Limit characteristic.
    """

    _template = Uint8Template()
