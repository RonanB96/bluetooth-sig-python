"""Anaerobic Heart Rate Upper Limit characteristic (0x2A82)."""

from __future__ import annotations

from ..constants import UINT8_MAX
from .base import BaseCharacteristic
from .templates import Uint8Template


class AnaerobicHeartRateUpperLimitCharacteristic(BaseCharacteristic):
    """Anaerobic Heart Rate Upper Limit characteristic (0x2A82).

    org.bluetooth.characteristic.anaerobic_heart_rate_upper_limit

    Anaerobic Heart Rate Upper Limit characteristic.
    """

    expected_length = 1
    min_value = 0
    max_value = UINT8_MAX
    expected_type = int

    _template = Uint8Template()
