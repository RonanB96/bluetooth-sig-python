"""Fitness Machine Control Point characteristic (0x2AD9)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

# Minimum data lengths for response parsing
_RESPONSE_OP_CODE_LENGTH = 2  # op_code(1) + response_op_code(1)
_RESPONSE_RESULT_LENGTH = 3  # op_code(1) + response_op_code(1) + result_code(1)


class FitnessMachineControlPointOpCode(IntEnum):
    """Fitness Machine Control Point operation codes per FTMS specification."""

    REQUEST_CONTROL = 0x00
    RESET = 0x01
    SET_TARGET_SPEED = 0x02
    SET_TARGET_INCLINATION = 0x03
    SET_TARGET_RESISTANCE_LEVEL = 0x04
    SET_TARGET_POWER = 0x05
    SET_TARGET_HEART_RATE = 0x06
    START_OR_RESUME = 0x07
    STOP_OR_PAUSE = 0x08
    SET_TARGETED_EXPENDED_ENERGY = 0x09
    SET_TARGETED_NUMBER_OF_STEPS = 0x0A
    SET_TARGETED_NUMBER_OF_STRIDES = 0x0B
    SET_TARGETED_DISTANCE = 0x0C
    SET_TARGETED_TRAINING_TIME = 0x0D
    SET_TARGETED_TIME_IN_TWO_HEART_RATE_ZONES = 0x0E
    SET_TARGETED_TIME_IN_THREE_HEART_RATE_ZONES = 0x0F
    SET_TARGETED_TIME_IN_FIVE_HEART_RATE_ZONES = 0x10
    SET_INDOOR_BIKE_SIMULATION_PARAMETERS = 0x11
    SET_WHEEL_CIRCUMFERENCE = 0x12
    SPIN_DOWN_CONTROL = 0x13
    SET_TARGETED_CADENCE = 0x14
    RESPONSE_CODE = 0x80


class FitnessMachineResultCode(IntEnum):
    """Fitness Machine Control Point result codes per FTMS specification."""

    SUCCESS = 0x01
    OP_CODE_NOT_SUPPORTED = 0x02
    INVALID_PARAMETER = 0x03
    OPERATION_FAILED = 0x04
    CONTROL_NOT_PERMITTED = 0x05


class FitnessMachineControlPointData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Fitness Machine Control Point characteristic.

    The parameter field contains opcode-specific data as raw bytes,
    or None for opcodes with no parameters.
    """

    op_code: FitnessMachineControlPointOpCode
    parameter: bytes | None = None
    response_op_code: FitnessMachineControlPointOpCode | None = None
    result_code: FitnessMachineResultCode | None = None


class FitnessMachineControlPointCharacteristic(BaseCharacteristic[FitnessMachineControlPointData]):
    """Fitness Machine Control Point characteristic (0x2AD9).

    org.bluetooth.characteristic.fitness_machine_control_point

    Used for control and configuration of fitness machines.
    Provides commands for starting, stopping, and setting targets.
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> FitnessMachineControlPointData:
        """Parse Fitness Machine Control Point data.

        Format: Op Code (uint8) + optional parameter (variable).

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext (may be None).
            validate: Whether to validate ranges (default True).

        Returns:
            FitnessMachineControlPointData containing parsed control point data.

        """
        op_code_raw = DataParser.parse_int8(data, 0, signed=False)
        op_code = FitnessMachineControlPointOpCode(op_code_raw)

        if op_code == FitnessMachineControlPointOpCode.RESPONSE_CODE:
            response_op_code = None
            result_code = None
            if len(data) >= _RESPONSE_OP_CODE_LENGTH:
                response_op_code = FitnessMachineControlPointOpCode(DataParser.parse_int8(data, 1, signed=False))
            if len(data) >= _RESPONSE_RESULT_LENGTH:
                result_code = FitnessMachineResultCode(DataParser.parse_int8(data, 2, signed=False))
            return FitnessMachineControlPointData(
                op_code=op_code,
                response_op_code=response_op_code,
                result_code=result_code,
            )

        parameter = bytes(data[1:]) if len(data) > 1 else None

        return FitnessMachineControlPointData(
            op_code=op_code,
            parameter=parameter,
        )

    def _encode_value(self, data: FitnessMachineControlPointData) -> bytearray:
        """Encode Fitness Machine Control Point data to bytes.

        Args:
            data: FitnessMachineControlPointData instance.

        Returns:
            Encoded bytes representing the control point command.

        """
        if not isinstance(data, FitnessMachineControlPointData):
            raise TypeError(f"Expected FitnessMachineControlPointData, got {type(data).__name__}")

        result = bytearray([int(data.op_code)])

        if data.op_code == FitnessMachineControlPointOpCode.RESPONSE_CODE:
            if data.response_op_code is not None:
                result.append(int(data.response_op_code))
            if data.result_code is not None:
                result.append(int(data.result_code))
        elif data.parameter is not None:
            result.extend(data.parameter)

        return result
