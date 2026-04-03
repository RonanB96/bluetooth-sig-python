"""Broadcast Audio Scan Control Point characteristic (0x2BC7)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class BroadcastAudioScanControlPointOpCode(IntEnum):
    """Broadcast Audio Scan Control Point operation codes."""

    REMOTE_SCAN_STOPPED = 0x00
    REMOTE_SCAN_STARTED = 0x01
    ADD_SOURCE = 0x02
    MODIFY_SOURCE = 0x03
    SET_BROADCAST_CODE = 0x04
    REMOVE_SOURCE = 0x05


class BroadcastAudioScanControlPointData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Broadcast Audio Scan Control Point characteristic.

    Contains the opcode and any additional parameters as raw bytes.
    """

    op_code: BroadcastAudioScanControlPointOpCode
    parameter_data: bytes = b""


class BroadcastAudioScanControlPointCharacteristic(BaseCharacteristic[BroadcastAudioScanControlPointData]):
    """Broadcast Audio Scan Control Point characteristic (0x2BC7).

    org.bluetooth.characteristic.broadcast_audio_scan_control_point

    Used for controlling broadcast audio scanning in the Broadcast
    Audio Scan Service.
    """

    _manual_role = CharacteristicRole.CONTROL
    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> BroadcastAudioScanControlPointData:
        """Parse Broadcast Audio Scan Control Point data.

        Format: opcode (uint8) + optional parameters.
        """
        op_code = BroadcastAudioScanControlPointOpCode(DataParser.parse_int8(data, 0, signed=False))
        parameter_data = bytes(data[1:]) if len(data) > 1 else b""

        return BroadcastAudioScanControlPointData(
            op_code=op_code,
            parameter_data=parameter_data,
        )

    def _encode_value(self, data: BroadcastAudioScanControlPointData) -> bytearray:
        """Encode Broadcast Audio Scan Control Point data to bytes."""
        result = bytearray()
        result += DataParser.encode_int8(int(data.op_code))
        result += bytearray(data.parameter_data)
        return result
