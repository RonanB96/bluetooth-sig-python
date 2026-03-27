"""LE HID Operation Mode characteristic (0x2C24).

Operation mode for LE HID devices.

References:
    Bluetooth SIG HID over GATT Profile specification
"""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class LEHIDOperationModeValue(IntEnum):
    """LE HID Operation Mode values."""

    REPORT_MODE = 0x00
    BOOT_MODE = 0x01


class LEHIDOperationModeCharacteristic(BaseCharacteristic[LEHIDOperationModeValue]):
    """LE HID Operation Mode characteristic (0x2C24).

    org.bluetooth.characteristic.le_hid_operation_mode

    Indicates the current operation mode of the LE HID device.
    """

    _characteristic_name = "LE HID Operation Mode"
    _template = EnumTemplate.uint8(LEHIDOperationModeValue)
