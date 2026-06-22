"""Voice Assistant Session State characteristic (0x2C35)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class VoiceAssistantSessionStateCharacteristic(BaseCharacteristic[int]):
    """Voice Assistant Session State characteristic (0x2C35).

    org.bluetooth.characteristic.voice_assistant_session_state
    """

    _template = Uint8Template()
