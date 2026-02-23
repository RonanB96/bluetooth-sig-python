"""Time Hour 24 characteristic (0x2B14)."""

from __future__ import annotations

from datetime import timedelta

from .base import BaseCharacteristic
from .templates import TimeDurationTemplate


class TimeHour24Characteristic(BaseCharacteristic[timedelta]):
    """Time Hour 24 characteristic (0x2B14).

    org.bluetooth.characteristic.time_hour_24

    Time in hours with a resolution of 1.
    A value of 0xFFFFFF represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFFFFFF).
    """

    _template = TimeDurationTemplate.hours_uint24()
