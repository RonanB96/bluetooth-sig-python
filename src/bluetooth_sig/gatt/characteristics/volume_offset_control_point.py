"""Volume Offset Control Point characteristic (0x2B82)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class VolumeOffsetControlPointOpCode(IntEnum):
    """Volume Offset Control Point operation codes."""

    SET_VOLUME_OFFSET = 0x01


_OFFSET_MINIMUM_LENGTH = 4


class VolumeOffsetControlPointData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Volume Offset Control Point characteristic.

    Contains the opcode, change counter, and optional volume offset parameter.
    """

    op_code: VolumeOffsetControlPointOpCode
    change_counter: int
    volume_offset: int | None = None


class VolumeOffsetControlPointCharacteristic(BaseCharacteristic[VolumeOffsetControlPointData]):
    """Volume Offset Control Point characteristic (0x2B82).

    org.bluetooth.characteristic.volume_offset_control_point

    Used for controlling volume offset in the Volume Offset Control Service.
    """

    _manual_role = CharacteristicRole.CONTROL
    min_length = 2
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> VolumeOffsetControlPointData:
        """Parse Volume Offset Control Point data.

        Format: opcode (uint8) + change_counter (uint8) + optional sint16 offset.
        """
        op_code = VolumeOffsetControlPointOpCode(DataParser.parse_int8(data, 0, signed=False))
        change_counter = DataParser.parse_int8(data, 1, signed=False)

        volume_offset = None
        if op_code == VolumeOffsetControlPointOpCode.SET_VOLUME_OFFSET and len(data) >= _OFFSET_MINIMUM_LENGTH:
            volume_offset = DataParser.parse_int16(data, 2, signed=True)

        return VolumeOffsetControlPointData(
            op_code=op_code,
            change_counter=change_counter,
            volume_offset=volume_offset,
        )

    def _encode_value(self, data: VolumeOffsetControlPointData) -> bytearray:
        """Encode Volume Offset Control Point data to bytes."""
        result = bytearray()
        result += DataParser.encode_int8(int(data.op_code))
        result += DataParser.encode_int8(data.change_counter)
        if data.volume_offset is not None:
            result += DataParser.encode_int16(data.volume_offset, signed=True)
        return result
