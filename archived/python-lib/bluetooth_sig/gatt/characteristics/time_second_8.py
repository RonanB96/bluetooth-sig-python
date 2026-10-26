"""Time Second 8 characteristic (0x2B16)."""

from __future__ import annotations

from datetime import timedelta

from .base import BaseCharacteristic
from .templates import TimeDurationTemplate


class TimeSecond8Characteristic(BaseCharacteristic[timedelta]):
    """Time Second 8 characteristic (0x2B16).

    org.bluetooth.characteristic.time_second_8

    Time in seconds with a resolution of 1 (0-254).
    A value of 0xFF represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFF).
    """

    _template = TimeDurationTemplate.seconds_uint8()
