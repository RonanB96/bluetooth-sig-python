"""ESL Control Point characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ESLCPOpcode(IntEnum):
    """ESL Control Point opcodes per ESL specification."""

    PING = 0x00
    UNASSOCIATE = 0x01
    SERVICE_RESET = 0x02
    FACTORY_RESET = 0x03
    UPDATE_COMPLETE = 0x04
    READ_SENSOR_DATA = 0x10
    REFRESH_DISPLAY = 0x11
    DISPLAY_IMAGE = 0x20
    DISPLAY_TIMED_IMAGE = 0x21
    LED_CONTROL = 0x30
    LED_TIMED_CONTROL = 0x31
    VENDOR_SPECIFIC = 0xFF


class ESLCPData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from ESL Control Point characteristic.

    Attributes:
        opcode: The ESL CP opcode.
        parameters: Raw parameter bytes (opcode-dependent).

    """

    opcode: ESLCPOpcode
    parameters: bytes = b""


class ESLControlPointCharacteristic(BaseCharacteristic[ESLCPData]):
    """ESL Control Point characteristic (0x2BFE).

    org.bluetooth.characteristic.esl_control_point

    Control point for Electronic Shelf Label operations.
    Complex multi-opcode characteristic supporting various ESL commands.
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
    ) -> ESLCPData:
        """Parse ESL CP data.

        Args:
            data: Raw bytes (1+ bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            ESLCPData with opcode and parameters.

        """
        opcode = ESLCPOpcode(DataParser.parse_int8(data, 0, signed=False))
        parameters = bytes(data[1:])
        return ESLCPData(opcode=opcode, parameters=parameters)

    def _encode_value(self, data: ESLCPData) -> bytearray:
        """Encode ESL CP data to bytes.

        Args:
            data: ESLCPData to encode.

        Returns:
            Encoded bytes.

        """
        result = DataParser.encode_int8(int(data.opcode), signed=False)
        result.extend(data.parameters)
        return result
