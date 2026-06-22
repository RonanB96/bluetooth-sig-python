"""Voice Assistant Supported Features characteristic (0x2C38)."""

from __future__ import annotations

from enum import IntFlag

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class VoiceAssistantSupportedFeatures(IntFlag):
    """Voice Assistant supported features bitfield."""

    TEXT_QUERY = 1 << 0
    VOICE_QUERY = 1 << 1
    MEDIA_CONTROL = 1 << 2
    SMART_HOME_CONTROL = 1 << 3
    CONTEXT_AWARE_RESPONSES = 1 << 4


class VoiceAssistantSupportedFeaturesCharacteristic(BaseCharacteristic[VoiceAssistantSupportedFeatures]):
    """Voice Assistant Supported Features characteristic (0x2C38).

    org.bluetooth.characteristic.voice_assistant_supported_features
    """

    min_length = 1
    max_length = 4
    allow_variable_length = True
    _UINT8_MAX = 0xFF
    _UINT16_MAX = 0xFFFF
    _UINT32_MAX = 0xFFFFFFFF

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> VoiceAssistantSupportedFeatures:
        raw = 0
        for i, byte in enumerate(data):
            raw |= byte << (8 * i)
        return VoiceAssistantSupportedFeatures(raw)

    def _encode_value(self, data: VoiceAssistantSupportedFeatures) -> bytearray:
        value = int(data)
        if value <= self._UINT8_MAX:
            return bytearray([value])
        if value <= self._UINT16_MAX:
            return bytearray([value & self._UINT8_MAX, (value >> 8) & self._UINT8_MAX])
        if value <= self._UINT32_MAX:
            return bytearray(
                [
                    value & self._UINT8_MAX,
                    (value >> 8) & self._UINT8_MAX,
                    (value >> 16) & self._UINT8_MAX,
                    (value >> 24) & self._UINT8_MAX,
                ]
            )
        raise ValueError("Voice Assistant Supported Features exceeds 32-bit range")
