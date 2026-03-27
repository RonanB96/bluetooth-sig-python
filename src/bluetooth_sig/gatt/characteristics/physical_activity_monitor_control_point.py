"""Physical Activity Monitor Control Point characteristic (0x2B43).

Control point for Physical Activity Monitor session management.

References:
    Bluetooth SIG Physical Activity Monitor Service 1.0
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class PAMControlPointOpCode(IntEnum):
    """Physical Activity Monitor Control Point Op Codes."""

    START_SESSION = 0x01
    STOP_SESSION = 0x02
    SET_ACTIVITY_TYPE = 0x03
    GET_ACTIVITY_TYPE = 0x04
    SET_SESSION_DESCRIPTOR = 0x05
    GET_SESSION_DESCRIPTOR = 0x06
    RESPONSE_CODE = 0x10


class PAMControlPointResponseCode(IntEnum):
    """Physical Activity Monitor Control Point response codes."""

    SUCCESS = 0x01
    OP_CODE_NOT_SUPPORTED = 0x02
    INVALID_PARAMETER = 0x03
    OPERATION_FAILED = 0x04
    PARAMETER_NOT_ALLOWED = 0x05


class PhysicalActivityMonitorControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Physical Activity Monitor Control Point.

    Attributes:
        opcode: The operation code.
        parameter: Raw parameter bytes (variable per opcode). Empty if none.

    """

    opcode: PAMControlPointOpCode
    parameter: bytes = b""


class PhysicalActivityMonitorControlPointCharacteristic(
    BaseCharacteristic[PhysicalActivityMonitorControlPointData],
):
    """Physical Activity Monitor Control Point characteristic (0x2B43).

    org.bluetooth.characteristic.physical_activity_monitor_control_point

    Control point for session management of the Physical Activity Monitor.
    ROLE: CONTROL
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> PhysicalActivityMonitorControlPointData:
        """Parse Physical Activity Monitor Control Point data.

        Format: OpCode (uint8) + Parameter (variable).
        """
        opcode = PAMControlPointOpCode(DataParser.parse_int8(data, 0, signed=False))
        parameter = bytes(data[1:])

        return PhysicalActivityMonitorControlPointData(
            opcode=opcode,
            parameter=parameter,
        )

    def _encode_value(self, data: PhysicalActivityMonitorControlPointData) -> bytearray:
        """Encode Physical Activity Monitor Control Point data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.opcode), signed=False))
        result.extend(data.parameter)
        return result
