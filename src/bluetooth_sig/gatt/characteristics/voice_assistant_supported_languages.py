"""Voice Assistant Supported Languages characteristic (0x2C37)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class VoiceAssistantSupportedLanguagesCharacteristic(BaseCharacteristic[str]):
    """Voice Assistant Supported Languages characteristic (0x2C37).

    org.bluetooth.characteristic.voice_assistant_supported_languages
    """

    _template = Utf8StringTemplate()
