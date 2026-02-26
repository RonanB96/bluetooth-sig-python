"""Fixed String 16 characteristic (0x2AF7)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class FixedString16Characteristic(BaseCharacteristic[str]):
    """Fixed String 16 characteristic (0x2AF7).

    org.bluetooth.characteristic.fixed_string_16

    Fixed-length 16-octet UTF-8 string.
    """

    _template = Utf8StringTemplate(max_length=16)
    expected_length = 16
