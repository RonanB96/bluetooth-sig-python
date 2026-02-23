"""Fixed String 36 characteristic (0x2AF5)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class FixedString36Characteristic(BaseCharacteristic[str]):
    """Fixed String 36 characteristic (0x2AF5).

    org.bluetooth.characteristic.fixed_string_36

    Fixed-length 36-octet UTF-8 string.
    """

    _template = Utf8StringTemplate(max_length=36)
    expected_length = 36
