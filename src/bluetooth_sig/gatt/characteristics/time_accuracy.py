"""Time Accuracy characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class TimeAccuracyCharacteristic(BaseCharacteristic[int]):
    """Time Accuracy characteristic (0x2A12).

    org.bluetooth.characteristic.time_accuracy

    Represents the accuracy of the time source in increments of 1/8 of a second.
    """

    _template = Uint8Template()
