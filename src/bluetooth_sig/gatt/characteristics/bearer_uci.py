"""Bearer UCI characteristic (0x2BB4)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class BearerUCICharacteristic(BaseCharacteristic[str]):
    """Bearer UCI characteristic (0x2BB4).

    org.bluetooth.characteristic.bearer_uci

    Bearer UCI characteristic.
    """

    _template = Utf8StringTemplate()
    min_length = 0
