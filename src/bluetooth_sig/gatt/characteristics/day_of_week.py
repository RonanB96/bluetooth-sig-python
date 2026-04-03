"""Day of Week characteristic implementation."""

from __future__ import annotations

from ...types.gatt_enums import DayOfWeek
from .base import BaseCharacteristic
from .templates import EnumTemplate


class DayOfWeekCharacteristic(BaseCharacteristic[DayOfWeek]):
    """Day of Week characteristic (0x2A09).

    org.bluetooth.characteristic.day_of_week

    Represents the day of the week as an 8-bit enumeration (1=Monday, 7=Sunday).
    """

    _template = EnumTemplate.uint8(DayOfWeek)
