"""DST Offset characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class DSTOffset(IntEnum):
    """DST Offset enumeration values."""

    STANDARD_TIME = 0
    HALF_HOUR_DAYLIGHT = 2
    DAYLIGHT_TIME = 4
    DOUBLE_DAYLIGHT = 8
    UNKNOWN = 255


class DstOffsetCharacteristic(BaseCharacteristic):
    """DST Offset characteristic (0x2A0D).

    org.bluetooth.characteristic.dst_offset

    Represents the Daylight Saving Time offset as an 8-bit enumeration.
    """

    _template = EnumTemplate.uint8(DSTOffset)
