"""Day of Week characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class DayOfWeekCharacteristic(BaseCharacteristic):
    """Day of Week characteristic (0x2A09).

    org.bluetooth.characteristic.day_of_week

    Represents the day of the week as an 8-bit enumeration (1=Monday, 7=Sunday).
    """

    _template = Uint8Template()
