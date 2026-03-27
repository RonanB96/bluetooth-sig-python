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

    READ_ACTIVE_BASAL_RATE = 0x01
    READ_ACTIVE_TBR = 0x02
    READ_ACTIVE_BOLUS_IDS = 0x03
    READ_ACTIVE_BOLUS_DELIVERY = 0x04
    READ_TOTAL_DAILY_INSULIN_STATUS = 0x05
    READ_COUNTER = 0x06
    READ_DELIVERED_INSULIN = 0x07
    RESPONSE_CODE = 0x10


class IDDStatusReaderResponseCode(IntEnum):
    """IDD Status Reader response codes."""

    SUCCESS = 0x01
    OP_CODE_NOT_SUPPORTED = 0x02
    INVALID_OPERAND = 0x03
    PROCEDURE_NOT_COMPLETED = 0x04


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

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> IDDStatusReaderControlPointData:
        """Parse IDD Status Reader Control Point data.

        Format: OpCode (uint8) + Parameter (variable).
        """
        opcode = IDDStatusReaderOpCode(DataParser.parse_int8(data, 0, signed=False))
        parameter = bytes(data[1:])

        return IDDStatusReaderControlPointData(
            opcode=opcode,
            parameter=parameter,
        )

    def _encode_value(self, data: IDDStatusReaderControlPointData) -> bytearray:
        """Encode IDD Status Reader Control Point data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.opcode), signed=False))
        result.extend(data.parameter)
        return result
