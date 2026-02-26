"""Door Window Status characteristic (0x2C12)."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class DoorWindowOpenStatus(IntEnum):
    """Door/window open status values.

    Values:
        OPEN: Door/window is open (0x00)
        CLOSED: Door/window is closed (0x01)
        TILTED_AJAR: Door/window is tilted or ajar (0x02)
    """

    OPEN = 0x00
    CLOSED = 0x01
    TILTED_AJAR = 0x02


class DoorWindowStatusCharacteristic(BaseCharacteristic[DoorWindowOpenStatus]):
    """Door Window Status characteristic (0x2C12).

    org.bluetooth.characteristic.door_window_status

    Reports the open/closed/tilted status of a door or window.
    """

    _template = EnumTemplate.uint8(DoorWindowOpenStatus)
