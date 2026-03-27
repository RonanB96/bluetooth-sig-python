"""Hearing Aid Preset Control Point characteristic (0x2BDB).

Control point for Hearing Aid presets.

References:
    Bluetooth SIG Hearing Access Service specification
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class HearingAidPresetControlPointOpCode(IntEnum):
    """Hearing Aid Preset Control Point Op Codes."""

    READ_PRESETS_REQUEST = 0x01
    READ_PRESET_RESPONSE = 0x02
    PRESET_CHANGED = 0x03
    WRITE_PRESET_NAME = 0x04
    SET_ACTIVE_PRESET = 0x05
    SET_NEXT_PRESET = 0x06
    SET_PREVIOUS_PRESET = 0x07
    SET_ACTIVE_PRESET_SYNCED_LOCALLY = 0x08
    SET_NEXT_PRESET_SYNCED_LOCALLY = 0x09
    SET_PREVIOUS_PRESET_SYNCED_LOCALLY = 0x0A


class HearingAidPresetControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Hearing Aid Preset Control Point.

    Attributes:
        opcode: The operation code.
        parameter: Raw parameter bytes (variable per opcode). Empty if none.

    """

    opcode: HearingAidPresetControlPointOpCode
    parameter: bytes = b""


class HearingAidPresetControlPointCharacteristic(
    BaseCharacteristic[HearingAidPresetControlPointData],
):
    """Hearing Aid Preset Control Point characteristic (0x2BDB).

    org.bluetooth.characteristic.hearing_aid_preset_control_point

    Control point for managing presets in the Hearing Access Service.
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> HearingAidPresetControlPointData:
        """Parse Hearing Aid Preset Control Point data.

        Format: OpCode (uint8) + Parameter (variable).
        """
        opcode = HearingAidPresetControlPointOpCode(DataParser.parse_int8(data, 0, signed=False))
        parameter = bytes(data[1:])

        return HearingAidPresetControlPointData(
            opcode=opcode,
            parameter=parameter,
        )

    def _encode_value(self, data: HearingAidPresetControlPointData) -> bytearray:
        """Encode Hearing Aid Preset Control Point data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.opcode), signed=False))
        result.extend(data.parameter)
        return result
