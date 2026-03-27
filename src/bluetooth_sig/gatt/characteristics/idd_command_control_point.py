"""IDD Command Control Point characteristic (0x2B25).

Control point for insulin delivery commands: bolus, TBR, profile management.

References:
    Bluetooth SIG Insulin Delivery Service 1.0
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class IDDCommandOpCode(IntEnum):
    """IDD Command Control Point Op Codes."""

    SNOOZE_ANNUNCIATION = 0x0100
    CONFIRM_ANNUNCIATION = 0x0101
    WRITE_BASAL_RATE_PROFILE_TEMPLATE = 0x0200
    READ_BASAL_RATE_PROFILE_TEMPLATE = 0x0201
    SET_TBR = 0x0300
    CANCEL_TBR = 0x0301
    GET_TBR_TEMPLATE = 0x0302
    SET_BOLUS = 0x0400
    CANCEL_BOLUS = 0x0401
    GET_AVAILABLE_BOLUSES = 0x0402
    GET_ACTIVE_BOLUS_IDS = 0x0403
    GET_ACTIVE_BOLUS_DELIVERY = 0x0404
    RESET_RESERVOIR_INSULIN_OPERATION_TIME = 0x0500
    READ_ISF_PROFILE_TEMPLATE = 0x0600
    WRITE_ISF_PROFILE_TEMPLATE = 0x0601
    READ_I2CHO_RATIO_PROFILE_TEMPLATE = 0x0700
    WRITE_I2CHO_RATIO_PROFILE_TEMPLATE = 0x0701
    READ_TARGET_GLUCOSE_RANGE_PROFILE_TEMPLATE = 0x0800
    WRITE_TARGET_GLUCOSE_RANGE_PROFILE_TEMPLATE = 0x0801
    GET_MAX_BOLUS_AMOUNT = 0x0900
    SET_MAX_BOLUS_AMOUNT = 0x0901
    RESPONSE_CODE = 0x0F00


class IDDCommandResponseCode(IntEnum):
    """IDD Command Control Point response codes."""

    SUCCESS = 0x01
    OP_CODE_NOT_SUPPORTED = 0x02
    INVALID_OPERAND = 0x03
    PROCEDURE_NOT_COMPLETED = 0x04
    PARAMETER_OUT_OF_RANGE = 0x05
    PROCEDURE_NOT_APPLICABLE = 0x06


class IDDCommandControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from IDD Command Control Point.

    Attributes:
        opcode: The operation code (uint16).
        operand: Raw operand bytes (variable per opcode). Empty if none.

    """

    opcode: IDDCommandOpCode
    operand: bytes = b""


class IDDCommandControlPointCharacteristic(BaseCharacteristic[IDDCommandControlPointData]):
    """IDD Command Control Point characteristic (0x2B25).

    org.bluetooth.characteristic.idd_command_control_point

    Control point for insulin delivery commands.
    ROLE: CONTROL
    """

    min_length = 2  # opcode is uint16
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> IDDCommandControlPointData:
        """Parse IDD Command Control Point data.

        Format: OpCode (uint16 LE) + Operand (variable).
        """
        opcode = IDDCommandOpCode(DataParser.parse_int16(data, 0, signed=False))
        operand = bytes(data[2:])

        return IDDCommandControlPointData(
            opcode=opcode,
            operand=operand,
        )

    def _encode_value(self, data: IDDCommandControlPointData) -> bytearray:
        """Encode IDD Command Control Point data."""
        result = bytearray()
        result.extend(DataParser.encode_int16(data.opcode, signed=False))
        result.extend(data.operand)
        return result
