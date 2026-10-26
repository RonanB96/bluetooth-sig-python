"""Time Second 16 characteristic (0x2B17)."""

from __future__ import annotations

from datetime import timedelta

from .base import BaseCharacteristic
from .templates import TimeDurationTemplate


class TimeSecond16Characteristic(BaseCharacteristic[timedelta]):
    """Time Second 16 characteristic (0x2B17).

    org.bluetooth.characteristic.time_second_16

    Time in seconds with a resolution of 1 (0-65534).
    A value of 0xFFFF represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFFFF).
    """

    _template = TimeDurationTemplate.seconds_uint16()
