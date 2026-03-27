"""ACS Control Point characteristic (0x2B33).

Control point for Audio Control Service operations.

References:
    Bluetooth SIG Audio Control Service
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ACSControlPointOpCode(IntEnum):
    """ACS Control Point operation codes."""

    SET_ACTIVE_PRESET = 0x01
    READ_PRESET_RECORD = 0x02
    WRITE_PRESET_NAME = 0x03
    SET_NEXT_PRESET = 0x04
    SET_PREVIOUS_PRESET = 0x05
    RESPONSE = 0xFF


class ACSControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from ACS Control Point characteristic.

    Attributes:
        opcode: ACS Control Point operation code.
        parameters: Raw parameter bytes.
    """

    opcode: ACSControlPointOpCode
    parameters: bytes = b""


class ACSControlPointCharacteristic(BaseCharacteristic[ACSControlPointData]):
    """ACS Control Point characteristic (0x2B33).

    org.bluetooth.characteristic.acs_control_point

    Control point for Audio Control Service operations.
    """

    _manual_role = CharacteristicRole.CONTROL
    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ACSControlPointData:
        """Parse ACS Control Point data.

        Format: OpCode (uint8) + Parameters (variable).
        """
        opcode = ACSControlPointOpCode(DataParser.parse_int8(data, 0, signed=False))
        parameters = bytes(data[1:])

        return ACSControlPointData(
            opcode=opcode,
            parameters=parameters,
        )

    def _encode_value(self, data: ACSControlPointData) -> bytearray:
        """Encode ACS Control Point data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.opcode), signed=False))
        result.extend(data.parameters)
        return result
