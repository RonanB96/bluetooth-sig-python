"""Voice Assistant Service Control Point characteristic (0x2C33)."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class VoiceAssistantServiceControlPointData(msgspec.Struct, frozen=True, kw_only=True):
    """Decoded Voice Assistant Service Control Point payload."""

    opcode: int
    parameter: bytes = b""


class VoiceAssistantServiceControlPointCharacteristic(BaseCharacteristic[VoiceAssistantServiceControlPointData]):
    """Voice Assistant Service Control Point characteristic (0x2C33).

    org.bluetooth.characteristic.voice_assistant_service_control_point

    Assigned Numbers defines an opcode plus optional parameters control-point
    structure for this characteristic.
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> VoiceAssistantServiceControlPointData:
        opcode = DataParser.parse_int8(data, 0, signed=False)
        return VoiceAssistantServiceControlPointData(opcode=opcode, parameter=bytes(data[1:]))

    def _encode_value(self, data: VoiceAssistantServiceControlPointData) -> bytearray:
        result = bytearray()
        result.extend(DataParser.encode_int8(data.opcode, signed=False))
        result.extend(data.parameter)
        return result
