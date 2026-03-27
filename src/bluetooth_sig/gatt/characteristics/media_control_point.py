"""Media Control Point characteristic (0x2BA4)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class MediaControlPointOpCode(IntEnum):
    """Media Control Point operation codes per MCS spec."""

    PLAY = 0x01
    PAUSE = 0x02
    FAST_REWIND = 0x03
    FAST_FORWARD = 0x04
    STOP = 0x05
    MOVE_RELATIVE = 0x06
    PREVIOUS_SEGMENT = 0x10
    NEXT_SEGMENT = 0x11
    FIRST_SEGMENT = 0x12
    LAST_SEGMENT = 0x13
    GOTO_SEGMENT = 0x14
    PREVIOUS_TRACK = 0x20
    NEXT_TRACK = 0x21
    FIRST_TRACK = 0x22
    LAST_TRACK = 0x23
    GOTO_TRACK = 0x24
    PREVIOUS_GROUP = 0x30
    NEXT_GROUP = 0x31
    FIRST_GROUP = 0x32
    LAST_GROUP = 0x33
    GOTO_GROUP = 0x34


# Opcodes that carry a sint32 parameter
_OPCODES_WITH_SINT32 = frozenset(
    {
        MediaControlPointOpCode.MOVE_RELATIVE,
        MediaControlPointOpCode.GOTO_SEGMENT,
        MediaControlPointOpCode.GOTO_TRACK,
        MediaControlPointOpCode.GOTO_GROUP,
    }
)

_SINT32_MINIMUM_LENGTH = 5


class MediaControlPointData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Media Control Point characteristic.

    The parameter field is present only for opcodes that require a sint32
    operand (Move Relative, Goto Segment, Goto Track, Goto Group).
    """

    op_code: MediaControlPointOpCode
    parameter: int | None = None


class MediaControlPointCharacteristic(BaseCharacteristic[MediaControlPointData]):
    """Media Control Point characteristic (0x2BA4).

    org.bluetooth.characteristic.media_control_point

    Used for controlling media playback in the Media Control Service.
    """

    _manual_role = CharacteristicRole.CONTROL
    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> MediaControlPointData:
        """Parse Media Control Point data.

        Format: opcode (uint8) + optional sint32 parameter.
        """
        op_code = MediaControlPointOpCode(DataParser.parse_int8(data, 0, signed=False))

        parameter = None
        if op_code in _OPCODES_WITH_SINT32 and len(data) >= _SINT32_MINIMUM_LENGTH:
            parameter = DataParser.parse_int32(data, 1, signed=True)

        return MediaControlPointData(op_code=op_code, parameter=parameter)

    def _encode_value(self, data: MediaControlPointData) -> bytearray:
        """Encode Media Control Point data to bytes."""
        result = bytearray()
        result += DataParser.encode_int8(int(data.op_code))
        if data.parameter is not None:
            result += DataParser.encode_int32(data.parameter, signed=True)
        return result
