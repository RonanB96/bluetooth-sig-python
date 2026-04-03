"""IDD Status Reader Control Point characteristic (0x2B24).

Control point for reading various IDD status fields.

References:
    Bluetooth SIG Insulin Delivery Service 1.0
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class IDDStatusReaderOpCode(IntEnum):
    """IDD Status Reader Control Point Op Codes."""

    RESPONSE_CODE = 0x0303
    RESET_STATUS = 0x030C
    GET_ACTIVE_BOLUS_IDS = 0x0330
    GET_ACTIVE_BOLUS_IDS_RESPONSE = 0x033F
    GET_ACTIVE_BOLUS_DELIVERY = 0x0356
    GET_ACTIVE_BOLUS_DELIVERY_RESPONSE = 0x0359
    GET_ACTIVE_BASAL_RATE_DELIVERY = 0x0365
    GET_ACTIVE_BASAL_RATE_DELIVERY_RESPONSE = 0x036A
    GET_TOTAL_DAILY_INSULIN_STATUS = 0x0395
    GET_TOTAL_DAILY_INSULIN_STATUS_RESPONSE = 0x039A
    GET_COUNTER = 0x03A6
    GET_COUNTER_RESPONSE = 0x03A9
    GET_DELIVERED_INSULIN = 0x03C0
    GET_DELIVERED_INSULIN_RESPONSE = 0x03CF
    GET_INSULIN_ON_BOARD = 0x03F3
    GET_INSULIN_ON_BOARD_RESPONSE = 0x03FC


class IDDStatusReaderResponseCode(IntEnum):
    """IDD Status Reader response codes."""

    SUCCESS = 0x0F
    OP_CODE_NOT_SUPPORTED = 0x70
    INVALID_OPERAND = 0x71
    PROCEDURE_NOT_COMPLETED = 0x72
    PARAMETER_OUT_OF_RANGE = 0x73
    PROCEDURE_NOT_APPLICABLE = 0x74


class IDDStatusReaderControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from IDD Status Reader Control Point.

    Attributes:
        opcode: The operation code.
        parameter: Raw parameter bytes (variable per opcode). Empty if none.

    """

    opcode: IDDStatusReaderOpCode
    parameter: bytes = b""


class IDDStatusReaderControlPointCharacteristic(BaseCharacteristic[IDDStatusReaderControlPointData]):
    """IDD Status Reader Control Point characteristic (0x2B24).

    org.bluetooth.characteristic.idd_status_reader_control_point

    Control point for reading IDD status information.
    ROLE: CONTROL
    """

    min_length = 2
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> IDDStatusReaderControlPointData:
        """Parse IDD Status Reader Control Point data.

        Format: OpCode (uint16) + Parameter (variable).
        """
        opcode = IDDStatusReaderOpCode(DataParser.parse_int16(data, 0, signed=False))
        parameter = bytes(data[2:])

        return IDDStatusReaderControlPointData(
            opcode=opcode,
            parameter=parameter,
        )

    def _encode_value(self, data: IDDStatusReaderControlPointData) -> bytearray:
        """Encode IDD Status Reader Control Point data."""
        result = bytearray()
        result.extend(DataParser.encode_int16(int(data.opcode), signed=False))
        result.extend(data.parameter)
        return result
