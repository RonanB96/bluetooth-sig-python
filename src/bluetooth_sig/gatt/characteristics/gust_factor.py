"""Gust Factor characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint8Template


class GustFactorCharacteristic(BaseCharacteristic):
    """Gust Factor characteristic (0x2A74).

    org.bluetooth.characteristic.gust_factor

    Represents the gust factor with 0.1 resolution (value * 0.1).
    """

    _template = ScaledUint8Template.from_letter_method(M=1, d=-1, b=0)  # 0.1 scaling
