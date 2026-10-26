"""Record Access Control Point characteristic (0x2A52).

Generic control point for managing stored records in services like
Glucose, CGM, and Blood Pressure.

References:
    Bluetooth SIG GATT Specification Supplement
    org.bluetooth.characteristic.record_access_control_point (GSS YAML)
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class RACPOpCode(IntEnum):
    """Record Access Control Point Op Codes."""

    REPORT_STORED_RECORDS = 0x01
    DELETE_STORED_RECORDS = 0x02
    ABORT_OPERATION = 0x03
    REPORT_NUMBER_OF_STORED_RECORDS = 0x04
    NUMBER_OF_STORED_RECORDS_RESPONSE = 0x05
    RESPONSE_CODE = 0x06
    COMBINED_REPORT = 0x07
    COMBINED_REPORT_RESPONSE = 0x08


class RACPOperator(IntEnum):
    """Record Access Control Point Operators."""

    NULL = 0x00
    ALL_RECORDS = 0x01
    LESS_THAN_OR_EQUAL_TO = 0x02
    GREATER_THAN_OR_EQUAL_TO = 0x03
    WITHIN_RANGE_OF = 0x04
    FIRST_RECORD = 0x05
    LAST_RECORD = 0x06


class RACPResponseCode(IntEnum):
    """Record Access Control Point Response Code Values."""

    SUCCESS = 0x01
    OP_CODE_NOT_SUPPORTED = 0x02
    INVALID_OPERATOR = 0x03
    OPERATOR_NOT_SUPPORTED = 0x04
    INVALID_OPERAND = 0x05
    NO_RECORDS_FOUND = 0x06
    ABORT_UNSUCCESSFUL = 0x07
    PROCEDURE_NOT_COMPLETED = 0x08
    OPERAND_NOT_SUPPORTED = 0x09


class RecordAccessControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Record Access Control Point.

    Attributes:
        opcode: The operation code.
        operator: The operator for the operation.
        operand: Raw operand bytes (service-specific). Empty if none.

    """

    opcode: RACPOpCode
    operator: RACPOperator
    operand: bytes = b""


class RecordAccessControlPointCharacteristic(BaseCharacteristic[RecordAccessControlPointData]):
    """Record Access Control Point characteristic (0x2A52).

    org.bluetooth.characteristic.record_access_control_point

    Generic control point for managing stored records.
    ROLE: CONTROL
    """

    min_length = 2  # OpCode(1) + Operator(1)
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> RecordAccessControlPointData:
        """Parse Record Access Control Point data.

        Format: OpCode (uint8) + Operator (uint8) + Operand (variable).
        """
        opcode = RACPOpCode(DataParser.parse_int8(data, 0, signed=False))
        operator = RACPOperator(DataParser.parse_int8(data, 1, signed=False))
        operand = bytes(data[2:])

        return RecordAccessControlPointData(
            opcode=opcode,
            operator=operator,
            operand=operand,
        )

    def _encode_value(self, data: RecordAccessControlPointData) -> bytearray:
        """Encode Record Access Control Point data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.opcode), signed=False))
        result.extend(DataParser.encode_int8(int(data.operator), signed=False))
        result.extend(data.operand)
        return result
