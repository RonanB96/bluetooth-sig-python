"""Fixed String 64 characteristic (0x2AF4)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class FixedString64Characteristic(BaseCharacteristic[str]):
    """Fixed String 64 characteristic (0x2AF4).

    org.bluetooth.characteristic.fixed_string_64

    Fixed-length 64-octet UTF-8 string.
    """

    _template = Utf8StringTemplate(max_length=64)
    expected_length = 64
