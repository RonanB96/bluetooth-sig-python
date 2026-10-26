"""Media State characteristic (0x2BA3)."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class MediaState(IntEnum):
    """Media player state."""

    INACTIVE = 0x00
    PLAYING = 0x01
    PAUSED = 0x02
    SEEKING = 0x03


class MediaStateCharacteristic(BaseCharacteristic[MediaState]):
    """Media State characteristic (0x2BA3).

    org.bluetooth.characteristic.media_state

    Current state of the media player.
    """

    expected_length: int = 1
    _template = EnumTemplate.uint8(MediaState)
