"""Audio Location characteristic (0x2B81)."""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class AudioLocation(IntFlag):
    """Audio location flags."""

    FRONT_LEFT = 0x00000001
    FRONT_RIGHT = 0x00000002
    FRONT_CENTER = 0x00000004
    LOW_FREQUENCY_EFFECTS_1 = 0x00000008
    BACK_LEFT = 0x00000010
    BACK_RIGHT = 0x00000020
    FRONT_LEFT_OF_CENTER = 0x00000040
    FRONT_RIGHT_OF_CENTER = 0x00000080
    BACK_CENTER = 0x00000100
    LOW_FREQUENCY_EFFECTS_2 = 0x00000200
    SIDE_LEFT = 0x00000400
    SIDE_RIGHT = 0x00000800
    TOP_FRONT_LEFT = 0x00001000
    TOP_FRONT_RIGHT = 0x00002000
    TOP_FRONT_CENTER = 0x00004000
    TOP_CENTER = 0x00008000
    TOP_BACK_LEFT = 0x00010000
    TOP_BACK_RIGHT = 0x00020000
    TOP_SIDE_LEFT = 0x00040000
    TOP_SIDE_RIGHT = 0x00080000
    TOP_BACK_CENTER = 0x00100000
    BOTTOM_FRONT_CENTER = 0x00200000
    BOTTOM_FRONT_LEFT = 0x00400000
    BOTTOM_FRONT_RIGHT = 0x00800000
    FRONT_LEFT_WIDE = 0x01000000
    FRONT_RIGHT_WIDE = 0x02000000
    LEFT_SURROUND = 0x04000000
    RIGHT_SURROUND = 0x08000000


class AudioLocationCharacteristic(BaseCharacteristic[AudioLocation]):
    """Audio Location characteristic (0x2B81).

    org.bluetooth.characteristic.audio_location

    Bitfield indicating the audio location channels.
    """

    _template = FlagTemplate.uint32(AudioLocation)
