"""Voice Assistant Session State characteristic (0x2C35)."""

from __future__ import annotations

from enum import IntEnum

from ..constants import SIZE_UINT8
from .base import BaseCharacteristic
from .templates import EnumTemplate


class VoiceAssistantSessionState(IntEnum):
    """Voice Assistant session state values."""

    SESSION_RESET = 0x00
    SESSION_UNAVAILABLE = 0x01
    SESSION_READY = 0x02
    SESSION_ACTIVE = 0x03


class VoiceAssistantSessionStateCharacteristic(BaseCharacteristic[VoiceAssistantSessionState]):
    """Voice Assistant Session State characteristic (0x2C35).

    org.bluetooth.characteristic.voice_assistant_session_state
    """

    expected_length = SIZE_UINT8
    _template = EnumTemplate.uint8(VoiceAssistantSessionState)
