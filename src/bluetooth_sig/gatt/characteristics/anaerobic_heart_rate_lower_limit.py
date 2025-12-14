"""Anaerobic Heart Rate Lower Limit characteristic (0x2A81)."""

from __future__ import annotations

from ..constants import UINT8_MAX
from .base import BaseCharacteristic
from .templates import Uint8Template


class AnaerobicHeartRateLowerLimitCharacteristic(BaseCharacteristic):
    """Anaerobic Heart Rate Lower Limit characteristic (0x2A81).

    org.bluetooth.characteristic.anaerobic_heart_rate_lower_limit

    Anaerobic Heart Rate Lower Limit characteristic.
    """

    expected_length = 1
    min_value = 0
    max_value = UINT8_MAX
    expected_type = int

    _template = Uint8Template()
