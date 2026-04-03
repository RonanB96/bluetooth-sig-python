"""SC Control Point characteristic (0x2A55).

Speed and Cadence sensor control point for calibration,
cumulative value, and sensor location management.

References:
    Bluetooth SIG Cycling Speed and Cadence / Running Speed and Cadence
    org.bluetooth.characteristic.sc_control_point (GSS YAML)
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class SCControlPointOpCode(IntEnum):
    """SC Control Point Op Codes."""

    SET_CUMULATIVE_VALUE = 0x01
    START_SENSOR_CALIBRATION = 0x02
    UPDATE_SENSOR_LOCATION = 0x03
    REQUEST_SUPPORTED_SENSOR_LOCATIONS = 0x04
    RESPONSE_CODE = 0x10


class SCControlPointResponseValue(IntEnum):
    """SC Control Point Response Values."""

    SUCCESS = 0x01
    OP_CODE_NOT_SUPPORTED = 0x02
    INVALID_PARAMETER = 0x03
    OPERATION_FAILED = 0x04


class SCControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from SC Control Point.

    Attributes:
        opcode: The operation code.
        parameter: Raw parameter bytes (variable per opcode). Empty if none.

    """

    opcode: SCControlPointOpCode
    parameter: bytes = b""


class SCControlPointCharacteristic(BaseCharacteristic[SCControlPointData]):
    """SC Control Point characteristic (0x2A55).

    org.bluetooth.characteristic.sc_control_point

    Control point for Speed and Cadence sensor procedures.
    ROLE: CONTROL
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> SCControlPointData:
        """Parse SC Control Point data.

        Format: OpCode (uint8) + Parameter (variable).
        """
        opcode = SCControlPointOpCode(DataParser.parse_int8(data, 0, signed=False))
        parameter = bytes(data[1:])

        return SCControlPointData(
            opcode=opcode,
            parameter=parameter,
        )

    def _encode_value(self, data: SCControlPointData) -> bytearray:
        """Encode SC Control Point data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.opcode), signed=False))
        result.extend(data.parameter)
        return result
