"""First Name characteristic (0x2A8B)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class FirstNameCharacteristic(BaseCharacteristic):
    """First Name characteristic (0x2A8B).

    org.bluetooth.characteristic.first_name

    First Name characteristic.
    """

    _template = Utf8StringTemplate()
    min_length = 0
