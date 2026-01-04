"""Serial Number String characteristic (0x2A25)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class SerialNumberStringCharacteristic(BaseCharacteristic[str]):
    """Serial Number String characteristic (0x2A25).

    org.bluetooth.characteristic.serial_number_string

    Serial Number String characteristic.
    """

    _template = Utf8StringTemplate()
