"""Aerobic Heart Rate Lower Limit characteristic (0x2A7E)."""

from __future__ import annotations

from ..constants import UINT8_MAX
from .base import BaseCharacteristic
from .templates import Uint8Template


class AerobicHeartRateLowerLimitCharacteristic(BaseCharacteristic):
    """Aerobic Heart Rate Lower Limit characteristic (0x2A7E).

    org.bluetooth.characteristic.aerobic_heart_rate_lower_limit

    Aerobic Heart Rate Lower Limit characteristic.
    """

    expected_length = 1
    min_value = 0
    max_value = UINT8_MAX
    expected_type = int

    _template = Uint8Template()
