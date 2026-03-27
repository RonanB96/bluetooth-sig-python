"""Call Friendly Name characteristic (0x2BC2)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class CallFriendlyNameCharacteristic(BaseCharacteristic[str]):
    """Call Friendly Name characteristic (0x2BC2).

    org.bluetooth.characteristic.call_friendly_name

    Call Friendly Name characteristic.
    """

    _template = Utf8StringTemplate()
    min_length = 0
