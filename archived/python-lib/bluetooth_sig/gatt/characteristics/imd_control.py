"""IMD Control characteristic (0x2C12).

Control point for Industrial Monitoring Device operations.

References:
    Bluetooth SIG Industrial Monitoring Device Service
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class IMDControlOpCode(IntEnum):
    """IMD Control operation codes."""

    RESET_DEVICE = 0x01
    START_MEASUREMENT = 0x02
    STOP_MEASUREMENT = 0x03
    CLEAR_STATUS = 0x04
    SET_CONFIGURATION = 0x05
    RESPONSE = 0xFF


class IMDControlData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from IMD Control characteristic.

    Attributes:
        opcode: IMD Control operation code.
        parameters: Raw parameter bytes.
    """

    opcode: IMDControlOpCode
    parameters: bytes = b""


class IMDControlCharacteristic(BaseCharacteristic[IMDControlData]):
    """IMD Control characteristic (0x2C12).

    org.bluetooth.characteristic.imd_control

    Control point for Industrial Monitoring Device operations.
    """

    _manual_role = CharacteristicRole.CONTROL
    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> IMDControlData:
        """Parse IMD Control data.

        Format: OpCode (uint8) + Parameters (variable).
        """
        opcode = IMDControlOpCode(DataParser.parse_int8(data, 0, signed=False))
        parameters = bytes(data[1:])

        return IMDControlData(
            opcode=opcode,
            parameters=parameters,
        )

    def _encode_value(self, data: IMDControlData) -> bytearray:
        """Encode IMD Control data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.opcode), signed=False))
        result.extend(data.parameters)
        return result
