"""Resting Heart Rate characteristic (0x2A92)."""

from __future__ import annotations

from ..constants import UINT8_MAX
from .base import BaseCharacteristic
from .templates import Uint8Template


class RestingHeartRateCharacteristic(BaseCharacteristic):
    """Resting Heart Rate characteristic (0x2A92).

    org.bluetooth.characteristic.resting_heart_rate

    Resting Heart Rate characteristic.
    """

    expected_length = 1
    min_value = 0
    max_value = UINT8_MAX
    expected_type = int

    _template = Uint8Template()
