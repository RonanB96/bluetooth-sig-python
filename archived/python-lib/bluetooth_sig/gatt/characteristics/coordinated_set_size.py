"""Coordinated Set Size characteristic (0x2B85)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class CoordinatedSetSizeCharacteristic(BaseCharacteristic[int]):
    """Coordinated Set Size characteristic (0x2B85).

    org.bluetooth.characteristic.size_characteristic

    The number of members in the coordinated set.
    """

    _template = Uint8Template()
