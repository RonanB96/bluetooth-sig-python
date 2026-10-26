"""Time Second 32 characteristic (0x2B18)."""

from __future__ import annotations

from datetime import timedelta

from .base import BaseCharacteristic
from .templates import TimeDurationTemplate


class TimeSecond32Characteristic(BaseCharacteristic[timedelta]):
    """Time Second 32 characteristic (0x2B18).

    org.bluetooth.characteristic.time_second_32

    Time in seconds with a resolution of 1 (0-4294967294).
    A value of 0xFFFFFFFF represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFFFFFFFF).
    """

    _template = TimeDurationTemplate.seconds_uint32()
