"""Mute characteristic."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class MuteState(IntEnum):
    """Mute state."""

    NOT_MUTED = 0
    MUTED = 1


class MuteCharacteristic(BaseCharacteristic[MuteState]):
    """Mute characteristic (0x2BC3).

    org.bluetooth.characteristic.mute

    Indicates whether the device is muted (1) or not muted (0).
    """

    expected_length: int = 1
    _template = EnumTemplate.uint8(MuteState)
