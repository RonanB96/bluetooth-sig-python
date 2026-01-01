"""Middle Name characteristic (0x2B48)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class MiddleNameCharacteristic(BaseCharacteristic):
    """Middle Name characteristic (0x2B48).

    org.bluetooth.characteristic.middle_name

    Middle Name characteristic.
    """

    _template = Utf8StringTemplate()
    min_length = 0
