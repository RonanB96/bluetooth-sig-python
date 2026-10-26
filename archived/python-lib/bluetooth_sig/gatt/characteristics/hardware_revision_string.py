"""Hardware Revision String characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class HardwareRevisionStringCharacteristic(BaseCharacteristic[str]):
    """Hardware Revision String characteristic (0x2A27).

    org.bluetooth.characteristic.hardware_revision_string

    Represents the hardware revision as a UTF-8 string.
    """

    _template = Utf8StringTemplate()
    min_length = 0
