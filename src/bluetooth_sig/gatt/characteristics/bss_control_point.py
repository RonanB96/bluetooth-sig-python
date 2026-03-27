"""BSS Control Point characteristic (0x2B2B).

Control point for the Broadcast Scan Service.

References:
    Bluetooth SIG Broadcast Audio Scan Service 1.0
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class BSSControlPointOpCode(IntEnum):
    """BSS Control Point Op Codes."""

    REMOTE_SCAN_STOPPED = 0x00
    REMOTE_SCAN_STARTED = 0x01
    ADD_SOURCE = 0x02
    MODIFY_SOURCE = 0x03
    SET_BROADCAST_CODE = 0x04
    REMOVE_SOURCE = 0x05


class BSSControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from BSS Control Point.

    Attributes:
        opcode: The operation code.
        parameter: Raw parameter bytes (variable per opcode). Empty if none.

    """

    opcode: BSSControlPointOpCode
    parameter: bytes = b""


class BSSControlPointCharacteristic(BaseCharacteristic[BSSControlPointData]):
    """BSS Control Point characteristic (0x2B2B).

    org.bluetooth.characteristic.bss_control_point

    Control point for managing broadcast audio sources in the
    Broadcast Scan Service.
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> BSSControlPointData:
        """Parse BSS Control Point data.

        Format: OpCode (uint8) + Parameter (variable).
        """
        opcode = BSSControlPointOpCode(DataParser.parse_int8(data, 0, signed=False))
        parameter = bytes(data[1:])

        return BSSControlPointData(
            opcode=opcode,
            parameter=parameter,
        )

    def _encode_value(self, data: BSSControlPointData) -> bytearray:
        """Encode BSS Control Point data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.opcode), signed=False))
        result.extend(data.parameter)
        return result
