"""Voice Assistant Service Control Point characteristic (0x2C33)."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..constants import SIZE_UINT8
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class VoiceAssistantControlPointOpcode(IntEnum):
    """VAS Control Point command opcodes."""

    INITIALIZE_SESSION = 0x00
    START_SESSION = 0x01
    STOP_SESSION = 0x02


class VoiceAssistantControlPointResponseOpcode(IntEnum):
    """VAS Control Point response opcode."""

    RESPONSE_CODE = 0x00


class VoiceAssistantControlPointResponseCode(IntEnum):
    """VAS Control Point response code values."""

    SUCCESS = 0x01
    OPCODE_NOT_SUPPORTED = 0x02
    OPERATION_FAILED = 0x03
    INVALID_SESSION_STATE = 0x04


class VoiceAssistantServiceControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Decoded Voice Assistant Service Control Point payload."""

    opcode: VoiceAssistantControlPointOpcode | VoiceAssistantControlPointResponseOpcode
    response_code: VoiceAssistantControlPointResponseCode | None = None


class VoiceAssistantServiceControlPointCharacteristic(BaseCharacteristic[VoiceAssistantServiceControlPointData]):
    """Voice Assistant Service Control Point characteristic (0x2C33).

    org.bluetooth.characteristic.voice_assistant_service_control_point

    Assigned Numbers defines an opcode plus optional parameters control-point
    structure for this characteristic.
    """

    min_length = SIZE_UINT8
    allow_variable_length = True
    _manual_role = CharacteristicRole.CONTROL

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> VoiceAssistantServiceControlPointData:
        opcode_raw = DataParser.parse_int8(data, 0, signed=False)
        parameter = bytes(data[SIZE_UINT8:])
        if opcode_raw == VoiceAssistantControlPointResponseOpcode.RESPONSE_CODE and parameter:
            if len(parameter) != SIZE_UINT8:
                raise ValueError("response code opcode requires one response-code byte")
            return VoiceAssistantServiceControlPointData(
                opcode=VoiceAssistantControlPointResponseOpcode.RESPONSE_CODE,
                response_code=VoiceAssistantControlPointResponseCode(parameter[0]),
            )

        opcode = VoiceAssistantControlPointOpcode(opcode_raw)
        self._validate_opcode_parameter(opcode, parameter, None)
        return VoiceAssistantServiceControlPointData(opcode=opcode)

    def _encode_value(self, data: VoiceAssistantServiceControlPointData) -> bytearray:
        self._validate_opcode_parameter(data.opcode, b"", data.response_code)
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.opcode), signed=False))
        if data.response_code is not None:
            result.extend(DataParser.encode_int8(int(data.response_code), signed=False))
        return result

    @staticmethod
    def _validate_opcode_parameter(
        opcode: VoiceAssistantControlPointOpcode | VoiceAssistantControlPointResponseOpcode,
        parameter: bytes,
        response_code: VoiceAssistantControlPointResponseCode | None,
    ) -> None:
        """Validate the opcode and parameter layout from VAS Tables 3.4 and 3.5."""
        if opcode == VoiceAssistantControlPointResponseOpcode.RESPONSE_CODE:
            if parameter:
                raise ValueError("response code is represented by response_code, not raw parameter bytes")
            return

        if opcode in {
            VoiceAssistantControlPointOpcode.INITIALIZE_SESSION,
            VoiceAssistantControlPointOpcode.START_SESSION,
            VoiceAssistantControlPointOpcode.STOP_SESSION,
        }:
            if parameter or response_code is not None:
                raise ValueError("VAS command opcodes do not include parameters")
            return

        raise ValueError("unsupported VAS control point opcode")
