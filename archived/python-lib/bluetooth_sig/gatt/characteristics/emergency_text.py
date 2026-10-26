"""Emergency Text characteristic (0x2B2E)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class EmergencyTextCharacteristic(BaseCharacteristic[str]):
    """Emergency Text characteristic (0x2B2E).

    org.bluetooth.characteristic.emergency_text

    1-20 octets of UTF-8 encoded text (no null terminator). Intended to
    carry human-readable information such as a name or phone number.
    Encryption required.
    """

    _template = Utf8StringTemplate()
    min_length: int = 1
    max_length: int = 20
