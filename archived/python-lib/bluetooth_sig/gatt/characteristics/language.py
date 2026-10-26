"""Language characteristic (0x2AA2)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class LanguageCharacteristic(BaseCharacteristic[str]):
    """Language characteristic (0x2AA2).

    org.bluetooth.characteristic.language

    Language characteristic.
    """

    _template = Utf8StringTemplate()
    min_length = 0
