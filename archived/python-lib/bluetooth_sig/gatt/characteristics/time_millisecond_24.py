"""Time Millisecond 24 characteristic (0x2B15)."""

from __future__ import annotations

from datetime import timedelta

from .base import BaseCharacteristic
from .templates import TimeDurationTemplate


class TimeMillisecond24Characteristic(BaseCharacteristic[timedelta]):
    """Time Millisecond 24 characteristic (0x2B15).

    org.bluetooth.characteristic.time_millisecond_24

    Time in milliseconds encoded as a 24-bit unsigned integer.
    Resolution is 0.001 seconds (1 ms).
    A value of 0xFFFFFF represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFFFFFF).
    """

    _template = TimeDurationTemplate.milliseconds_uint24()
