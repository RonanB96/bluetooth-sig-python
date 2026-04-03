"""Seeking Speed characteristic (0x2B9B)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Sint8Template


class SeekingSpeedCharacteristic(BaseCharacteristic[int]):
    """Seeking Speed characteristic (0x2B9B).

    org.bluetooth.characteristic.seeking_speed

    Signed 8-bit seeking speed factor.
    """

    _template = Sint8Template()
