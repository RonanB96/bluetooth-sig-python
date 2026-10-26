"""Media Control Point Opcodes Supported characteristic (0x2BA5)."""

from __future__ import annotations

from enum import IntFlag

from .base import BaseCharacteristic
from .templates import FlagTemplate


class MediaControlPointOpcodes(IntFlag):
    """Supported media control point opcodes."""

    PLAY = 0x00000001
    PAUSE = 0x00000002
    FAST_REWIND = 0x00000004
    FAST_FORWARD = 0x00000008
    STOP = 0x00000010
    MOVE_RELATIVE = 0x00000020
    PREVIOUS_SEGMENT = 0x00000040
    NEXT_SEGMENT = 0x00000080
    FIRST_SEGMENT = 0x00000100
    LAST_SEGMENT = 0x00000200
    GOTO_SEGMENT = 0x00000400
    PREVIOUS_TRACK = 0x00000800
    NEXT_TRACK = 0x00001000
    FIRST_TRACK = 0x00002000
    LAST_TRACK = 0x00004000
    GOTO_TRACK = 0x00008000
    PREVIOUS_GROUP = 0x00010000
    NEXT_GROUP = 0x00020000
    FIRST_GROUP = 0x00040000
    LAST_GROUP = 0x00080000
    GOTO_GROUP = 0x00100000


class MediaControlPointOpcodesSupportedCharacteristic(BaseCharacteristic[MediaControlPointOpcodes]):
    """Media Control Point Opcodes Supported characteristic (0x2BA5).

    org.bluetooth.characteristic.media_control_point_opcodes_supported

    Bitfield indicating the supported media control point opcodes.
    """

    _template = FlagTemplate.uint32(MediaControlPointOpcodes)
