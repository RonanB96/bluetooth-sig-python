"""URI characteristic (0x2AB6)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class URICharacteristic(BaseCharacteristic[str]):
    """URI characteristic (0x2AB6).

    org.bluetooth.characteristic.uri

    URI characteristic.
    """

    _template = Utf8StringTemplate()
    min_length = 0
