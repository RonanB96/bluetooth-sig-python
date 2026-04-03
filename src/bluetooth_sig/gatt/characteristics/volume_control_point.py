"""Volume Control Point characteristic (0x2B7E)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class VolumeControlPointOpCode(IntEnum):
    """Volume Control Point operation codes."""

    RELATIVE_VOLUME_DOWN = 0x00
    RELATIVE_VOLUME_UP = 0x01
    UNMUTE_RELATIVE_VOLUME_DOWN = 0x02
    UNMUTE_RELATIVE_VOLUME_UP = 0x03
    SET_ABSOLUTE_VOLUME = 0x04
    UNMUTE = 0x05
    MUTE = 0x06


_VOLUME_SETTING_MINIMUM_LENGTH = 3


class VolumeControlPointData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Volume Control Point characteristic.

    The parameter field contains opcode-specific data as raw bytes,
    or None for opcodes with no additional parameters beyond change_counter.
    """

    op_code: VolumeControlPointOpCode
    change_counter: int
    volume_setting: int | None = None


class VolumeControlPointCharacteristic(BaseCharacteristic[VolumeControlPointData]):
    """Volume Control Point characteristic (0x2B7E).

    org.bluetooth.characteristic.volume_control_point

    Used for controlling volume settings in the Volume Control Service.
    """

    _manual_role = CharacteristicRole.CONTROL
    min_length = 2
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> VolumeControlPointData:
        """Parse Volume Control Point data.

        Format: opcode (uint8) + change_counter (uint8) + optional parameter.
        """
        op_code = VolumeControlPointOpCode(DataParser.parse_int8(data, 0, signed=False))
        change_counter = DataParser.parse_int8(data, 1, signed=False)

        volume_setting = None
        if op_code == VolumeControlPointOpCode.SET_ABSOLUTE_VOLUME and len(data) >= _VOLUME_SETTING_MINIMUM_LENGTH:
            volume_setting = DataParser.parse_int8(data, 2, signed=False)

        return VolumeControlPointData(
            op_code=op_code,
            change_counter=change_counter,
            volume_setting=volume_setting,
        )

    def _encode_value(self, data: VolumeControlPointData) -> bytearray:
        """Encode Volume Control Point data to bytes."""
        result = bytearray()
        result += DataParser.encode_int8(int(data.op_code))
        result += DataParser.encode_int8(data.change_counter)
        if data.volume_setting is not None:
            result += DataParser.encode_int8(data.volume_setting)
        return result
