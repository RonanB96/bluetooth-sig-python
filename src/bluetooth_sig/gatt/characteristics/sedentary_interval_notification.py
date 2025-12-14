"""Sedentary Interval Notification characteristic (0x2B4F)."""

from __future__ import annotations

from ..constants import UINT16_MAX
from .base import BaseCharacteristic
from .templates import Uint16Template


class SedentaryIntervalNotificationCharacteristic(BaseCharacteristic):
    """Sedentary Interval Notification characteristic (0x2B4F).

    org.bluetooth.characteristic.sedentary_interval_notification

    Sedentary Interval Notification characteristic.
    """

    _template = Uint16Template()

    # Validation attributes
    expected_length: int = 2
    min_value: int = 0
    max_value: int = UINT16_MAX
    expected_type: type = int
