"""Time Exponential 8 characteristic (0x2B13)."""

from __future__ import annotations

from datetime import timedelta

from .base import BaseCharacteristic
from .templates import TimeExponentialTemplate


class TimeExponential8Characteristic(BaseCharacteristic[timedelta]):
    """Time Exponential 8 characteristic (0x2B13).

    org.bluetooth.characteristic.time_exponential_8

    Time duration using exponential encoding: value = 1.1^(N - 64) seconds.
    - Raw 0x00 represents 0 seconds.
    - Raw 0xFE represents total life of the device.
    - Raw 0xFF represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFE, 0xFF).
    """

    _template = TimeExponentialTemplate()
