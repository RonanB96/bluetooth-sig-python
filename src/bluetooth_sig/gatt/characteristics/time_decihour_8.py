"""Time Decihour 8 characteristic (0x2B12)."""

from __future__ import annotations

from datetime import timedelta

from .base import BaseCharacteristic
from .templates import TimeDurationTemplate


class TimeDecihour8Characteristic(BaseCharacteristic[timedelta]):
    """Time Decihour 8 characteristic (0x2B12).

    org.bluetooth.characteristic.time_decihour_8

    Time in hours with a resolution of 0.1 (deci-hours).
    M=1, d=-1, b=0 → scale factor 0.1.
    Range: 0.0-23.9. A value of 0xFF represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFF).
    """

    _template = TimeDurationTemplate.decihours_uint8()
