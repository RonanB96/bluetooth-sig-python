"""Last Name characteristic (0x2A91)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class LastNameCharacteristic(BaseCharacteristic[str]):
    """Last Name characteristic (0x2A91).

    org.bluetooth.characteristic.last_name

    Last Name characteristic.
    """

    _template = Utf8StringTemplate()
    min_length = 0
