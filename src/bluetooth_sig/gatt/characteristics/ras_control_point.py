"""RAS Control Point characteristic (0x2C17).

Control point for Ranging Service operations.

References:
    Bluetooth SIG Ranging Service
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class RASControlPointOpCode(IntEnum):
    """RAS Control Point operation codes (RAS v1.0 Table 3.10)."""

    GET_RANGING_DATA = 0x00
    ACK_RANGING_DATA = 0x01
    RETRIEVE_LOST_SEGMENTS = 0x02
    ABORT_OPERATION = 0x03
    SET_FILTER = 0x04


class RASControlPointResponseOpCode(IntEnum):
    """RAS Control Point response operation codes (RAS v1.0 Table 3.11)."""

    COMPLETE_RANGING_DATA_RESPONSE = 0x00
    COMPLETE_LOST_SEGMENT_RESPONSE = 0x01
    RESPONSE_CODE = 0x02


class RASControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from RAS Control Point characteristic.

    Attributes:
        opcode: RAS Control Point operation code.
        parameters: Raw parameter bytes.
    """

    opcode: RASControlPointOpCode
    parameters: bytes = b""


class RASControlPointCharacteristic(BaseCharacteristic[RASControlPointData]):
    """RAS Control Point characteristic (0x2C17).

    org.bluetooth.characteristic.ras_control_point

    Control point for Ranging Service operations.
    """

    _manual_role = CharacteristicRole.CONTROL
    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> RASControlPointData:
        """Parse RAS Control Point data.

        Format: OpCode (uint8) + Parameters (variable).
        """
        opcode = RASControlPointOpCode(DataParser.parse_int8(data, 0, signed=False))
        parameters = bytes(data[1:])

        return RASControlPointData(
            opcode=opcode,
            parameters=parameters,
        )

    def _encode_value(self, data: RASControlPointData) -> bytearray:
        """Encode RAS Control Point data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.opcode), signed=False))
        result.extend(data.parameters)
        return result
