"""User Control Point characteristic (0x2A9F).

Control point for the User Data Service.

References:
    Bluetooth SIG User Data Service 1.0
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class UserControlPointOpCode(IntEnum):
    """User Control Point Op Codes."""

    REGISTER_NEW_USER = 0x01
    CONSENT = 0x02
    DELETE_USER_DATA = 0x03
    LIST_ALL_USERS = 0x04
    DELETE_USER = 0x05
    RESPONSE = 0x20


class UserControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from User Control Point.

    Attributes:
        opcode: The operation code.
        parameter: Raw parameter bytes (variable per opcode). Empty if none.

    """

    opcode: UserControlPointOpCode
    parameter: bytes = b""


class UserControlPointCharacteristic(BaseCharacteristic[UserControlPointData]):
    """User Control Point characteristic (0x2A9F).

    org.bluetooth.characteristic.user_control_point

    Control point for user management in the User Data Service.
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> UserControlPointData:
        """Parse User Control Point data.

        Format: OpCode (uint8) + Parameter (variable).
        """
        opcode = UserControlPointOpCode(DataParser.parse_int8(data, 0, signed=False))
        parameter = bytes(data[1:])

        return UserControlPointData(
            opcode=opcode,
            parameter=parameter,
        )

    def _encode_value(self, data: UserControlPointData) -> bytearray:
        """Encode User Control Point data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.opcode), signed=False))
        result.extend(data.parameter)
        return result
