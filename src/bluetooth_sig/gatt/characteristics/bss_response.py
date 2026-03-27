"""BSS Response characteristic (0x2B2C).

Response characteristic for the Broadcast Scan Service.

References:
    Bluetooth SIG Broadcast Audio Scan Service 1.0
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class BSSResponseOpCode(IntEnum):
    """BSS Response Op Codes (mirrors control point opcodes)."""

    REMOTE_SCAN_STOPPED = 0x00
    REMOTE_SCAN_STARTED = 0x01
    ADD_SOURCE = 0x02
    MODIFY_SOURCE = 0x03
    SET_BROADCAST_CODE = 0x04
    REMOVE_SOURCE = 0x05


class BSSResponseResult(IntEnum):
    """BSS Response result codes."""

    SUCCESS = 0x00
    OPCODE_NOT_SUPPORTED = 0x01
    INVALID_SOURCE_ID = 0x02


class BSSResponseData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from BSS Response.

    Attributes:
        opcode: The operation code being responded to.
        result: The result code.

    """

    opcode: BSSResponseOpCode
    result: BSSResponseResult


class BSSResponseCharacteristic(BaseCharacteristic[BSSResponseData]):
    """BSS Response characteristic (0x2B2C).

    org.bluetooth.characteristic.bss_response

    Response characteristic for the Broadcast Scan Service control point.
    """

    min_length = 2

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> BSSResponseData:
        """Parse BSS Response data.

        Format: OpCode (uint8) + Result (uint8).
        """
        opcode = BSSResponseOpCode(DataParser.parse_int8(data, 0, signed=False))
        result = BSSResponseResult(DataParser.parse_int8(data, 1, signed=False))

        return BSSResponseData(
            opcode=opcode,
            result=result,
        )

    def _encode_value(self, data: BSSResponseData) -> bytearray:
        """Encode BSS Response data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.opcode), signed=False))
        result.extend(DataParser.encode_int8(int(data.result), signed=False))
        return result
