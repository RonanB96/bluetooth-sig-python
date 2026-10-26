"""Playback Speed characteristic (0x2B9A)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Sint8Template


class PlaybackSpeedCharacteristic(BaseCharacteristic[int]):
    """Playback Speed characteristic (0x2B9A).

    org.bluetooth.characteristic.playback_speed

    Signed 8-bit playback speed factor.
    """

    _template = Sint8Template()
