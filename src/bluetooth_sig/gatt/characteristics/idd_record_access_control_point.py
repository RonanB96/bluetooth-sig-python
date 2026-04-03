"""IDD Record Access Control Point characteristic (0x2B27).

IDD-specific record access control point for managing insulin delivery
history records. Same pattern as generic RACP (0x2A52) but IDD-specific.

References:
    Bluetooth SIG Insulin Delivery Service 1.0.1, Table 3.21, 3.25
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class IDDRACPOpCode(IntEnum):
    """IDD Record Access Control Point Op Codes (Table 3.25, Hamming codes)."""

    RESPONSE_CODE = 0x0F
    REPORT_STORED_RECORDS = 0x33
    DELETE_STORED_RECORDS = 0x3C
    ABORT_OPERATION = 0x55
    REPORT_NUMBER_OF_STORED_RECORDS = 0x5A
    NUMBER_OF_STORED_RECORDS_RESPONSE = 0x66


class IDDRACPOperator(IntEnum):
    """IDD Record Access Control Point Operators (Table 3.26, Hamming codes)."""

    NULL = 0x0F
    ALL_RECORDS = 0x33
    LESS_THAN_OR_EQUAL = 0x3C
    GREATER_THAN_OR_EQUAL = 0x55
    RANGE_INCLUSIVE = 0x5A
    FIRST_RECORD = 0x66
    LAST_RECORD = 0x69


class IDDRACPResponseCode(IntEnum):
    """IDD RACP response codes (Table 3.27)."""

    # Error codes 0x02-0x09 range (from generic RACP)
    UNSUPPORTED_OPERATOR = 0x02
    INVALID_OPERATOR = 0x03
    UNSUPPORTED_OPERAND = 0x04
    INVALID_OPERAND = 0x05
    UNCLEAR_OPERATOR = 0x06
    # IDD-specific codes
    PROCEDURE_NOT_APPLICABLE = 0x0A
    SUCCESS = 0xF0


class IDDRecordAccessControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from IDD Record Access Control Point.

    Attributes:
        opcode: The operation code.
        operator: The operator for the operation.
        operand: Raw operand bytes. Empty if none.

    """

    opcode: IDDRACPOpCode
    operator: IDDRACPOperator
    operand: bytes = b""


class IDDRecordAccessControlPointCharacteristic(BaseCharacteristic[IDDRecordAccessControlPointData]):
    """IDD Record Access Control Point characteristic (0x2B27).

    org.bluetooth.characteristic.idd_record_access_control_point

    IDD-specific record access control point.
    ROLE: CONTROL
    """

    min_length = 2  # OpCode(1) + Operator(1)
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> IDDRecordAccessControlPointData:
        """Parse IDD RACP data.

        Format: OpCode (uint8) + Operator (uint8) + Operand (variable).
        """
        opcode = IDDRACPOpCode(DataParser.parse_int8(data, 0, signed=False))
        operator = IDDRACPOperator(DataParser.parse_int8(data, 1, signed=False))
        operand = bytes(data[2:])

        return IDDRecordAccessControlPointData(
            opcode=opcode,
            operator=operator,
            operand=operand,
        )

    def _encode_value(self, data: IDDRecordAccessControlPointData) -> bytearray:
        """Encode IDD RACP data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.opcode), signed=False))
        result.extend(DataParser.encode_int8(int(data.operator), signed=False))
        result.extend(data.operand)
        return result
