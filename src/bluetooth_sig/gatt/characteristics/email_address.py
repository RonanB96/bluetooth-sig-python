"""Email Address characteristic (0x2A88)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class EmailAddressCharacteristic(BaseCharacteristic):
    """Email Address characteristic (0x2A88).

    org.bluetooth.characteristic.email_address

    Email Address characteristic.
    """

    _template = Utf8StringTemplate()
    min_length = 0
