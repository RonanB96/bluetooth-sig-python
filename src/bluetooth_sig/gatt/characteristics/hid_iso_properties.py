"""HID ISO Properties characteristic (0x2C23).

Bitfield for HID Isochronous properties.

References:
    Bluetooth SIG HID over GATT Profile specification
"""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class HIDISOProperties(IntFlag):
    """HID ISO Properties flags."""

    INPUT_REPORT_SUPPORTED = 0x01
    OUTPUT_REPORT_SUPPORTED = 0x02


class HIDISOPropertiesCharacteristic(BaseCharacteristic[HIDISOProperties]):
    """HID ISO Properties characteristic (0x2C23).

    org.bluetooth.characteristic.hid_iso_properties

    Bitfield indicating supported HID isochronous channel properties.
    """

    _characteristic_name = "HID ISO Properties"
    _template = FlagTemplate.uint8(HIDISOProperties)
