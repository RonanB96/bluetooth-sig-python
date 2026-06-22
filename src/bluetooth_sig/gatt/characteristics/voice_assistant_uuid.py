"""Voice Assistant UUID characteristic (0x2C32)."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class VoiceAssistantUUIDCharacteristic(BaseCharacteristic[bytes]):
    """Voice Assistant UUID characteristic (0x2C32).

    org.bluetooth.characteristic.voice_assistant_uuid

    This characteristic exposes a 128-bit UUID that identifies
    the voice assistant instance.
    """

    expected_length = 16
    _UUID_LENGTH = 16

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> bytes:
        return bytes(data)

    def _encode_value(self, data: bytes) -> bytearray:
        if len(data) != self._UUID_LENGTH:
            raise ValueError("voice assistant UUID must be exactly 16 bytes")
        return bytearray(data)
