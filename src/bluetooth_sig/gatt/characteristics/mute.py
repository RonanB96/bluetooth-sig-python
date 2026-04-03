"""Mute characteristic."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class MuteState(IntEnum):
    """Mute state (MICS v1.0, Section 3.1)."""

    NOT_MUTED = 0x00
    MUTED = 0x01
    DISABLED = 0x02


class MuteCharacteristic(BaseCharacteristic[MuteState]):
    """Mute characteristic (0x2BC3).

    org.bluetooth.characteristic.mute

    Indicates whether the device is muted (1) or not muted (0).
    """

    expected_length: int = 1
    _template = EnumTemplate.uint8(MuteState)
