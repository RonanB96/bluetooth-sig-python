"""Voice Assistant Session Flag characteristic (0x2C36)."""

from __future__ import annotations

from enum import IntFlag

from ..constants import SIZE_UINT8
from .base import BaseCharacteristic
from .templates import FlagTemplate


class VoiceAssistantSessionFlags(IntFlag):
    """Voice Assistant session flags."""

    LISTENING_NOW = 1 << 0
    PROCESSING_NOW = 1 << 1
    PLAYBACK_NOW = 1 << 2


class VoiceAssistantSessionFlagCharacteristic(BaseCharacteristic[VoiceAssistantSessionFlags]):
    """Voice Assistant Session Flag characteristic (0x2C36).

    org.bluetooth.characteristic.voice_assistant_session_flag
    """

    expected_length = SIZE_UINT8
    _template = FlagTemplate.uint8(VoiceAssistantSessionFlags)
