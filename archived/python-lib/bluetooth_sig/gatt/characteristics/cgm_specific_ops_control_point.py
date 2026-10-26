"""CGM Specific Ops Control Point characteristic (0x2AAC).

Control point for CGM-specific procedures: communication interval,
calibration, alert levels, session control.

References:
    Bluetooth SIG Continuous Glucose Monitoring Service
    org.bluetooth.characteristic.cgm_specific_ops_control_point (GSS YAML)
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class CGMSpecificOpsOpCode(IntEnum):
    """CGM Specific Ops Control Point Op Codes."""

    SET_CGM_COMMUNICATION_INTERVAL = 0x01
    GET_CGM_COMMUNICATION_INTERVAL = 0x02
    CGM_COMMUNICATION_INTERVAL_RESPONSE = 0x03
    SET_GLUCOSE_CALIBRATION_VALUE = 0x04
    GET_GLUCOSE_CALIBRATION_VALUE = 0x05
    GLUCOSE_CALIBRATION_VALUE_RESPONSE = 0x06
    SET_PATIENT_HIGH_ALERT_LEVEL = 0x07
    GET_PATIENT_HIGH_ALERT_LEVEL = 0x08
    PATIENT_HIGH_ALERT_LEVEL_RESPONSE = 0x09
    SET_PATIENT_LOW_ALERT_LEVEL = 0x0A
    GET_PATIENT_LOW_ALERT_LEVEL = 0x0B
    PATIENT_LOW_ALERT_LEVEL_RESPONSE = 0x0C
    SET_HYPO_ALERT_LEVEL = 0x0D
    GET_HYPO_ALERT_LEVEL = 0x0E
    HYPO_ALERT_LEVEL_RESPONSE = 0x0F
    SET_HYPER_ALERT_LEVEL = 0x10
    GET_HYPER_ALERT_LEVEL = 0x11
    HYPER_ALERT_LEVEL_RESPONSE = 0x12
    SET_RATE_OF_DECREASE_ALERT_LEVEL = 0x13
    GET_RATE_OF_DECREASE_ALERT_LEVEL = 0x14
    RATE_OF_DECREASE_ALERT_LEVEL_RESPONSE = 0x15
    SET_RATE_OF_INCREASE_ALERT_LEVEL = 0x16
    GET_RATE_OF_INCREASE_ALERT_LEVEL = 0x17
    RATE_OF_INCREASE_ALERT_LEVEL_RESPONSE = 0x18
    RESET_DEVICE_SPECIFIC_ALERT = 0x19
    START_THE_SESSION = 0x1A
    STOP_THE_SESSION = 0x1B
    RESPONSE_CODE = 0x1C


class CGMSpecificOpsResponseCode(IntEnum):
    """CGM Specific Ops response codes."""

    SUCCESS = 0x01
    OP_CODE_NOT_SUPPORTED = 0x02
    INVALID_OPERAND = 0x03
    PROCEDURE_NOT_COMPLETED = 0x04
    PARAMETER_OUT_OF_RANGE = 0x05


class CGMSpecificOpsControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from CGM Specific Ops Control Point.

    Attributes:
        opcode: The operation code.
        operand: Raw operand bytes (variable per opcode). Empty if none.
        e2e_crc: Optional E2E-CRC (present if CGM Feature indicates support).

    """

    opcode: CGMSpecificOpsOpCode
    operand: bytes = b""
    e2e_crc: int | None = None


class CGMSpecificOpsControlPointCharacteristic(BaseCharacteristic[CGMSpecificOpsControlPointData]):
    """CGM Specific Ops Control Point characteristic (0x2AAC).

    org.bluetooth.characteristic.cgm_specific_ops_control_point

    Used to enable procedures related to a continuous glucose monitor.
    ROLE: CONTROL
    """

    _manual_role = None  # Let classifier infer CONTROL from name
    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> CGMSpecificOpsControlPointData:
        """Parse CGM Specific Ops Control Point data.

        Format: OpCode (uint8) + Operand (variable) + optional E2E-CRC (uint16).

        The E2E-CRC, if present, occupies the last 2 bytes. Without external
        knowledge of CRC support we cannot distinguish a 2-byte operand tail
        from a CRC, so we always treat the last 2 bytes as CRC when >= 3 bytes
        total and the opcode is a response type or the data length suggests it.
        For simplicity, CRC is *not* split out here — consumers should use
        CGM Feature to decide whether CRC is present.
        """
        opcode = CGMSpecificOpsOpCode(DataParser.parse_int8(data, 0, signed=False))
        operand = bytes(data[1:])

        return CGMSpecificOpsControlPointData(
            opcode=opcode,
            operand=operand,
        )

    def _encode_value(self, data: CGMSpecificOpsControlPointData) -> bytearray:
        """Encode CGM Specific Ops Control Point data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.opcode), signed=False))
        result.extend(data.operand)
        if data.e2e_crc is not None:
            result.extend(DataParser.encode_int16(data.e2e_crc, signed=False))
        return result
