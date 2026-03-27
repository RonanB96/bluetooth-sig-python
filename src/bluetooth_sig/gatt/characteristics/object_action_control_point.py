"""Object Action Control Point characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class OACPOpcode(IntEnum):
    """Object Action Control Point opcodes per OTS specification."""

    CREATE = 0x01
    DELETE = 0x02
    CALCULATE_CHECKSUM = 0x03
    EXECUTE = 0x04
    READ = 0x05
    WRITE = 0x06
    ABORT = 0x07
    RESPONSE = 0x60


class OACPResultCode(IntEnum):
    """OACP response result codes per OTS specification."""

    SUCCESS = 0x01
    OPCODE_NOT_SUPPORTED = 0x02
    INVALID_PARAMETER = 0x03
    INSUFFICIENT_RESOURCES = 0x04
    INVALID_OBJECT = 0x05
    CHANNEL_UNAVAILABLE = 0x06
    UNSUPPORTED_TYPE = 0x07
    PROCEDURE_NOT_PERMITTED = 0x08
    OBJECT_LOCKED = 0x09
    OPERATION_FAILED = 0x0A


class OACPData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Object Action Control Point characteristic.

    Attributes:
        opcode: The OACP opcode.
        parameters: Raw parameter bytes (opcode-dependent).

    """

    opcode: OACPOpcode
    parameters: bytes = b""


class ObjectActionControlPointCharacteristic(BaseCharacteristic[OACPData]):
    """Object Action Control Point characteristic (0x2AC5).

    org.bluetooth.characteristic.object_action_control_point

    Control point for object actions in the Object Transfer Service (OTS).
    Opcodes include Create, Delete, Calculate Checksum, Execute, Read,
    Write, Abort, and Response.
    """

    _manual_role = CharacteristicRole.CONTROL
    min_length: int = 1  # At minimum: opcode (1 byte)
    allow_variable_length: bool = True

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> OACPData:
        """Parse OACP data.

        Args:
            data: Raw bytes (1+ bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            OACPData with opcode and parameters.

        """
        opcode = OACPOpcode(DataParser.parse_int8(data, 0, signed=False))
        parameters = bytes(data[1:])
        return OACPData(opcode=opcode, parameters=parameters)

    def _encode_value(self, data: OACPData) -> bytearray:
        """Encode OACP data to bytes.

        Args:
            data: OACPData to encode.

        Returns:
            Encoded bytes.

        """
        result = DataParser.encode_int8(int(data.opcode), signed=False)
        result.extend(data.parameters)
        return result
