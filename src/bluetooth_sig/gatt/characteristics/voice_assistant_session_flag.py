"""Voice Assistant Session Flag characteristic (0x2C36)."""

from __future__ import annotations

from enum import IntFlag

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class VoiceAssistantSessionFlags(IntFlag):
    """Voice Assistant session state flags.

    Assigned Numbers lists this characteristic as a session flag bitfield.
    """

    SESSION_ACTIVE = 1 << 0
    USER_INTERACTION_REQUIRED = 1 << 1
    PRIVACY_MODE_ENABLED = 1 << 2


class VoiceAssistantSessionFlagCharacteristic(BaseCharacteristic[VoiceAssistantSessionFlags]):
    """Voice Assistant Session Flag characteristic (0x2C36).

    org.bluetooth.characteristic.voice_assistant_session_flag
    """

    min_length = 1
    max_length = 2
    allow_variable_length = True
    _UINT8_MAX = 0xFF
    _UINT16_MAX = 0xFFFF

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> VoiceAssistantSessionFlags:
        raw = 0
        for i, byte in enumerate(data):
            raw |= byte << (8 * i)
        return VoiceAssistantSessionFlags(raw)

    def _encode_value(self, data: VoiceAssistantSessionFlags) -> bytearray:
        value = int(data)
        if value <= self._UINT8_MAX:
            return bytearray([value])
        if value <= self._UINT16_MAX:
            return bytearray([value & self._UINT8_MAX, (value >> 8) & self._UINT8_MAX])
        raise ValueError("Voice Assistant Session Flag value exceeds 16-bit range")
