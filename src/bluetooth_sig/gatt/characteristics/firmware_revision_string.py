"""Firmware Revision String characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class FirmwareRevisionStringCharacteristic(BaseCharacteristic):
    """Firmware Revision String characteristic (0x2A26).

    org.bluetooth.characteristic.firmware_revision_string

    Represents the firmware revision as a UTF-8 string.
    """

    _template = Utf8StringTemplate()
    min_length = 0
