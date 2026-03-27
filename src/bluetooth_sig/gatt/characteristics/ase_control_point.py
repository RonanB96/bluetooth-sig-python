"""ASE Control Point characteristic (0x2BC6)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ASEControlPointOpCode(IntEnum):
    """ASE Control Point operation codes."""

    CONFIG_CODEC = 0x01
    CONFIG_QOS = 0x02
    ENABLE = 0x03
    RECEIVER_START_READY = 0x04
    DISABLE = 0x05
    RECEIVER_STOP_READY = 0x06
    UPDATE_METADATA = 0x07
    RELEASE = 0x08
    RESPONSE = 0xFF


class ASEControlPointData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from ASE Control Point characteristic.

    Contains the opcode, number of ASEs, and any additional
    ASE-specific parameters as raw bytes.
    """

    op_code: ASEControlPointOpCode
    number_of_ases: int
    parameter_data: bytes = b""


_HEADER_SIZE = 2  # opcode (uint8) + number_of_ases (uint8)


class ASEControlPointCharacteristic(BaseCharacteristic[ASEControlPointData]):
    """ASE Control Point characteristic (0x2BC6).

    org.bluetooth.characteristic.ase_control_point

    Used for controlling Audio Stream Endpoints in the Audio
    Stream Control Service.
    """

    _manual_role = CharacteristicRole.CONTROL
    min_length = 2
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ASEControlPointData:
        """Parse ASE Control Point data.

        Format: opcode (uint8) + number_of_ases (uint8) + ASE-specific params.
        """
        op_code = ASEControlPointOpCode(DataParser.parse_int8(data, 0, signed=False))
        number_of_ases = DataParser.parse_int8(data, 1, signed=False)
        parameter_data = bytes(data[_HEADER_SIZE:]) if len(data) > _HEADER_SIZE else b""

        return ASEControlPointData(
            op_code=op_code,
            number_of_ases=number_of_ases,
            parameter_data=parameter_data,
        )

    def _encode_value(self, data: ASEControlPointData) -> bytearray:
        """Encode ASE Control Point data to bytes."""
        result = bytearray()
        result += DataParser.encode_int8(int(data.op_code))
        result += DataParser.encode_int8(data.number_of_ases)
        result += bytearray(data.parameter_data)
        return result
