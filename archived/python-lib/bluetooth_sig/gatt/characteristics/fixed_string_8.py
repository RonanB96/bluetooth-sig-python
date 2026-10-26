"""Fixed String 8 characteristic (0x2AF8)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class FixedString8Characteristic(BaseCharacteristic[str]):
    """Fixed String 8 characteristic (0x2AF8).

    org.bluetooth.characteristic.fixed_string_8

    Fixed-length 8-octet UTF-8 string.
    """

    _template = Utf8StringTemplate(max_length=8)
    expected_length = 8
