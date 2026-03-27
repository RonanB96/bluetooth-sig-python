"""GHS Control Point characteristic (0x2BF4).

Control point for the Generic Health Sensor service.

References:
    Bluetooth SIG Generic Health Sensor Service specification
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class GHSControlPointOpCode(IntEnum):
    """GHS Control Point Op Codes."""

    START_SEND_LIVE_OBSERVATIONS = 0x01
    STOP_SEND_LIVE_OBSERVATIONS = 0x02
    START_SEND_STORED_OBSERVATIONS = 0x03
    STOP_SEND_STORED_OBSERVATIONS = 0x04
    DELETE_STORED_OBSERVATIONS = 0x05
    RESPONSE_CODE = 0x06


class GHSControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from GHS Control Point.

    Attributes:
        opcode: The operation code.
        parameter: Raw parameter bytes (variable per opcode). Empty if none.

    """

    opcode: GHSControlPointOpCode
    parameter: bytes = b""


class GHSControlPointCharacteristic(BaseCharacteristic[GHSControlPointData]):
    """GHS Control Point characteristic (0x2BF4).

    org.bluetooth.characteristic.ghs_control_point

    Control point for managing observations in the Generic Health
    Sensor service.
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> GHSControlPointData:
        """Parse GHS Control Point data.

        Format: OpCode (uint8) + Parameter (variable).
        """
        opcode = GHSControlPointOpCode(DataParser.parse_int8(data, 0, signed=False))
        parameter = bytes(data[1:])

        return GHSControlPointData(
            opcode=opcode,
            parameter=parameter,
        )

    def _encode_value(self, data: GHSControlPointData) -> bytearray:
        """Encode GHS Control Point data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.opcode), signed=False))
        result.extend(data.parameter)
        return result
