"""Fixed String 24 characteristic (0x2AF6)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class FixedString24Characteristic(BaseCharacteristic[str]):
    """Fixed String 24 characteristic (0x2AF6).

    org.bluetooth.characteristic.fixed_string_24

    Fixed-length 24-octet UTF-8 string.
    """

    _template = Utf8StringTemplate(max_length=24)
    expected_length = 24
