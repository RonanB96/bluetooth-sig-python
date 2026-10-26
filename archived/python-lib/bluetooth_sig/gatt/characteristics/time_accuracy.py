"""Time Accuracy characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint8Template


class TimeAccuracyCharacteristic(BaseCharacteristic[float]):
    """Time Accuracy characteristic (0x2A12).

    org.bluetooth.characteristic.time_accuracy

    Represents the accuracy (drift) of time information in seconds.
    M=1, d=0, b=-3 → scale factor 1/8 (0.125s per raw unit).
    Valid range: 0-253 raw (0s to 31.625s).
    Raw 254 = drift > 31.625s, raw 255 = unknown.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFE, 0xFF).
    """

    _template = ScaledUint8Template.from_letter_method(M=1, d=0, b=-3)
