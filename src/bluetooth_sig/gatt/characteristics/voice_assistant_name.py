"""Voice Assistant Name characteristic (0x2C31)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class VoiceAssistantNameCharacteristic(BaseCharacteristic[str]):
    """Voice Assistant Name characteristic (0x2C31).

    org.bluetooth.characteristic.voice_assistant_name
    """

    _template = Utf8StringTemplate()
