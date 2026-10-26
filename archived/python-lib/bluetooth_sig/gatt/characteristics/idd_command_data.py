"""IDD Command Data characteristic (0x2B26).

Contains command data associated with IDD Command Control Point responses.

References:
    Bluetooth SIG Insulin Delivery Service 1.0
"""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .idd_command_control_point import IDDCommandOpCode
from .utils import DataParser


class IDDCommandDataPayload(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from IDD Command Data characteristic.

    Attributes:
        opcode: The echoed operation code (uint16 LE).
        command_data: Raw command-specific data bytes.

    """

    opcode: IDDCommandOpCode
    command_data: bytes = b""


class IDDCommandDataCharacteristic(BaseCharacteristic[IDDCommandDataPayload]):
    """IDD Command Data characteristic (0x2B26).

    org.bluetooth.characteristic.idd_command_data

    Contains command data associated with IDD Command Control Point operations.
    """

    min_length = 2  # opcode (uint16)
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> IDDCommandDataPayload:
        """Parse IDD Command Data.

        Format: OpCode (uint16 LE) + CommandData (variable).
        """
        opcode = IDDCommandOpCode(DataParser.parse_int16(data, 0, signed=False))
        command_data = bytes(data[2:])

        return IDDCommandDataPayload(
            opcode=opcode,
            command_data=command_data,
        )

    def _encode_value(self, data: IDDCommandDataPayload) -> bytearray:
        """Encode IDD Command Data."""
        result = bytearray()
        result.extend(DataParser.encode_int16(data.opcode, signed=False))
        result.extend(data.command_data)
        return result
