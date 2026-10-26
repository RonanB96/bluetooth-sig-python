"""Fitness Machine Status characteristic (0x2ADA)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class FitnessMachineStatusOpCode(IntEnum):
    """Fitness Machine Status operation codes per FTMS specification."""

    RESET = 0x01
    FITNESS_MACHINE_STOPPED_OR_PAUSED_BY_USER = 0x02
    FITNESS_MACHINE_STOPPED_BY_SAFETY_KEY = 0x03
    FITNESS_MACHINE_STARTED_OR_RESUMED_BY_USER = 0x04
    TARGET_SPEED_CHANGED = 0x05
    TARGET_INCLINATION_CHANGED = 0x06
    TARGET_RESISTANCE_LEVEL_CHANGED = 0x07
    TARGET_POWER_CHANGED = 0x08
    TARGET_HEART_RATE_CHANGED = 0x09
    TARGETED_EXPENDED_ENERGY_CHANGED = 0x0A
    TARGETED_NUMBER_OF_STEPS_CHANGED = 0x0B
    TARGETED_NUMBER_OF_STRIDES_CHANGED = 0x0C
    TARGETED_DISTANCE_CHANGED = 0x0D
    TARGETED_TRAINING_TIME_CHANGED = 0x0E
    TARGETED_TIME_IN_TWO_HEART_RATE_ZONES_CHANGED = 0x0F
    TARGETED_TIME_IN_THREE_HEART_RATE_ZONES_CHANGED = 0x10
    TARGETED_TIME_IN_FIVE_HEART_RATE_ZONES_CHANGED = 0x11
    INDOOR_BIKE_SIMULATION_PARAMETERS_CHANGED = 0x12
    WHEEL_CIRCUMFERENCE_CHANGED = 0x13
    SPIN_DOWN_STATUS = 0x14
    TARGETED_CADENCE_CHANGED = 0x15
    CONTROL_PERMISSION_LOST = 0xFF


class FitnessMachineStatusData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Fitness Machine Status characteristic.

    The parameter field contains opcode-specific data as raw bytes,
    or None for opcodes with no parameters.
    """

    op_code: FitnessMachineStatusOpCode
    parameter: bytes | None = None


class FitnessMachineStatusCharacteristic(BaseCharacteristic[FitnessMachineStatusData]):
    """Fitness Machine Status characteristic (0x2ADA).

    org.bluetooth.characteristic.fitness_machine_status

    Notifies the client about status changes of the fitness machine,
    including target setting changes and machine state transitions.
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> FitnessMachineStatusData:
        """Parse Fitness Machine Status data.

        Format: Op Code (uint8) + optional parameter (variable).

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext (may be None).
            validate: Whether to validate ranges (default True).

        Returns:
            FitnessMachineStatusData containing parsed status data.

        """
        op_code_raw = DataParser.parse_int8(data, 0, signed=False)
        op_code = FitnessMachineStatusOpCode(op_code_raw)

        parameter = bytes(data[1:]) if len(data) > 1 else None

        return FitnessMachineStatusData(
            op_code=op_code,
            parameter=parameter,
        )

    def _encode_value(self, data: FitnessMachineStatusData) -> bytearray:
        """Encode Fitness Machine Status data to bytes.

        Args:
            data: FitnessMachineStatusData instance.

        Returns:
            Encoded bytes representing the status notification.

        """
        result = bytearray([int(data.op_code)])

        if data.parameter is not None:
            result.extend(data.parameter)

        return result
