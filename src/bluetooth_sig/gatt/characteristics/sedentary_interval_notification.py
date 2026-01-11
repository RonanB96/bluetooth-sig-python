"""Sedentary Interval Notification characteristic (0x2B4F)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint16Template


class SedentaryIntervalNotificationCharacteristic(BaseCharacteristic[int]):
    """Sedentary Interval Notification characteristic (0x2B4F).

    org.bluetooth.characteristic.sedentary_interval_notification

    Sedentary Interval Notification characteristic.
    """

    _template = Uint16Template()

    # Validation attributes
