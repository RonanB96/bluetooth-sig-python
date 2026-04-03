"""IDD Command Control Point characteristic (0x2B25).

Control point for insulin delivery commands: bolus, TBR, profile management.

References:
    Bluetooth SIG Insulin Delivery Service 1.0.1, Table 4.36
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class IDDCommandOpCode(IntEnum):
    """IDD Command Control Point Op Codes (Table 4.36, IDS v1.0.1)."""

    RESPONSE_CODE = 0x0F55
    SET_THERAPY_CONTROL_STATE = 0x0F5A
    SET_FLIGHT_MODE = 0x0F66
    SNOOZE_ANNUNCIATION = 0x0F69
    SNOOZE_ANNUNCIATION_RESPONSE = 0x0F96
    CONFIRM_ANNUNCIATION = 0x0F99
    CONFIRM_ANNUNCIATION_RESPONSE = 0x0FA5
    READ_BASAL_RATE_PROFILE_TEMPLATE = 0x0FAA
    READ_BASAL_RATE_PROFILE_TEMPLATE_RESPONSE = 0x0FC3
    WRITE_BASAL_RATE_PROFILE_TEMPLATE = 0x0FCC
    WRITE_BASAL_RATE_PROFILE_TEMPLATE_RESPONSE = 0x0FF0
    SET_TBR_ADJUSTMENT = 0x0FFF
    CANCEL_TBR_ADJUSTMENT = 0x1111
    GET_TBR_TEMPLATE = 0x111E
    GET_TBR_TEMPLATE_RESPONSE = 0x1122
    SET_TBR_TEMPLATE = 0x112D
    SET_TBR_TEMPLATE_RESPONSE = 0x1144
    SET_BOLUS = 0x114B
    SET_BOLUS_RESPONSE = 0x1177
    CANCEL_BOLUS = 0x11A4  # NOTE: value not explicitly in spec extract; retained
    GET_AVAILABLE_BOLUSES = 0x11C3  # NOTE: value not explicitly in spec extract; retained
    GET_AVAILABLE_BOLUSES_RESPONSE = 0x11B4
    GET_BOLUS_TEMPLATE = 0x11BB
    GET_BOLUS_TEMPLATE_RESPONSE = 0x11D2
    SET_BOLUS_TEMPLATE = 0x11DD
    SET_BOLUS_TEMPLATE_RESPONSE = 0x11E1
    GET_TEMPLATE_STATUS_AND_DETAILS = 0x11EE
    GET_TEMPLATE_STATUS_AND_DETAILS_RESPONSE = 0x1212
    RESET_TEMPLATE_STATUS = 0x121D
    RESET_TEMPLATE_STATUS_RESPONSE = 0x1221
    ACTIVATE_PROFILE_TEMPLATES = 0x122E
    ACTIVATE_PROFILE_TEMPLATES_RESPONSE = 0x1247
    GET_ACTIVATED_PROFILE_TEMPLATES = 0x1248
    GET_ACTIVATED_PROFILE_TEMPLATES_RESPONSE = 0x1274
    START_PRIMING = 0x127B
    STOP_PRIMING = 0x1284
    SET_INITIAL_RESERVOIR_FILL_LEVEL = 0x128B
    RESET_RESERVOIR_INSULIN_OPERATION_TIME = 0x12B7
    READ_ISF_PROFILE_TEMPLATE = 0x12B8
    READ_ISF_PROFILE_TEMPLATE_RESPONSE = 0x12D1
    WRITE_ISF_PROFILE_TEMPLATE = 0x12DE
    WRITE_ISF_PROFILE_TEMPLATE_RESPONSE = 0x12E2
    READ_I2CHO_RATIO_PROFILE_TEMPLATE = 0x12ED
    READ_I2CHO_RATIO_PROFILE_TEMPLATE_RESPONSE = 0x1414
    WRITE_I2CHO_RATIO_PROFILE_TEMPLATE = 0x141B
    WRITE_I2CHO_RATIO_PROFILE_TEMPLATE_RESPONSE = 0x1427
    READ_TARGET_GLUCOSE_RANGE_PROFILE_TEMPLATE = 0x1428
    READ_TARGET_GLUCOSE_RANGE_PROFILE_TEMPLATE_RESPONSE = 0x1441
    WRITE_TARGET_GLUCOSE_RANGE_PROFILE_TEMPLATE = 0x144E
    WRITE_TARGET_GLUCOSE_RANGE_PROFILE_TEMPLATE_RESPONSE = 0x1472
    GET_MAX_BOLUS_AMOUNT = 0x147D
    GET_MAX_BOLUS_AMOUNT_RESPONSE = 0x1482
    SET_MAX_BOLUS_AMOUNT = 0x148D


class IDDCommandResponseCode(IntEnum):
    """IDD Command Control Point response codes (Table 4.38, Hamming distance 4 to 0x0F)."""

    SUCCESS = 0x0F
    OP_CODE_NOT_SUPPORTED = 0x70
    INVALID_OPERAND = 0x71
    PROCEDURE_NOT_COMPLETED = 0x72
    PARAMETER_OUT_OF_RANGE = 0x73
    PROCEDURE_NOT_APPLICABLE = 0x74
    PLAUSIBILITY_CHECK_FAILED = 0x75
    MAXIMUM_BOLUS_NUMBER_REACHED = 0x76


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
