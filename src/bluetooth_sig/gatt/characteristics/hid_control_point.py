"""HID Control Point characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate

# Constants per Bluetooth HID specification
HID_CONTROL_POINT_DATA_LENGTH = 1  # Fixed data length: 1 byte


class HidControlPointCommand(IntEnum):
    """HID Control Point commands."""

    SUSPEND = 0
    EXIT_SUSPEND = 1


class HidControlPointCharacteristic(BaseCharacteristic):
    """HID Control Point characteristic (0x2A4C).

    org.bluetooth.characteristic.hid_control_point

    HID Control Point characteristic.
    """

    _template = EnumTemplate.uint8(HidControlPointCommand)
    expected_length = HID_CONTROL_POINT_DATA_LENGTH
