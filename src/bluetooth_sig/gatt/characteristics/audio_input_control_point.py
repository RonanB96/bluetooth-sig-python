"""Audio Input Control Point characteristic (0x2B7B)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class AudioInputControlPointOpCode(IntEnum):
    """Audio Input Control Point operation codes."""

    SET_GAIN_SETTING = 0x01
    UNMUTE = 0x02
    MUTE = 0x03
    SET_MANUAL_GAIN_MODE = 0x04
    SET_AUTOMATIC_GAIN_MODE = 0x05


class AudioInputControlPointData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Audio Input Control Point characteristic.

    The gain_setting field is present only for SET_GAIN_SETTING opcode.
    """

    op_code: AudioInputControlPointOpCode
    change_counter: int
    gain_setting: int | None = None


_MIN_LENGTH_WITH_GAIN = 3  # opcode (uint8) + change_counter (uint8) + gain_setting (int8)


class AudioInputControlPointCharacteristic(BaseCharacteristic[AudioInputControlPointData]):
    """Audio Input Control Point characteristic (0x2B7B).

    org.bluetooth.characteristic.audio_input_control_point

    Used for controlling audio input settings in the Audio Input Control Service.
    """

    _manual_role = CharacteristicRole.CONTROL
    min_length = 2
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> AudioInputControlPointData:
        """Parse Audio Input Control Point data.

        Format: opcode (uint8) + change_counter (uint8) + optional parameter.
        """
        op_code = AudioInputControlPointOpCode(DataParser.parse_int8(data, 0, signed=False))
        change_counter = DataParser.parse_int8(data, 1, signed=False)

        gain_setting = None
        if op_code == AudioInputControlPointOpCode.SET_GAIN_SETTING and len(data) >= _MIN_LENGTH_WITH_GAIN:
            gain_setting = DataParser.parse_int8(data, 2, signed=True)

        return AudioInputControlPointData(
            op_code=op_code,
            change_counter=change_counter,
            gain_setting=gain_setting,
        )

    def _encode_value(self, data: AudioInputControlPointData) -> bytearray:
        """Encode Audio Input Control Point data to bytes."""
        result = bytearray()
        result += DataParser.encode_int8(int(data.op_code))
        result += DataParser.encode_int8(data.change_counter)
        if data.gain_setting is not None:
            result += DataParser.encode_int8(data.gain_setting, signed=True)
        return result
