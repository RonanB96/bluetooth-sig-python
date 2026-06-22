"""Voice Assistant Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class VoiceAssistantService(BaseGattService):
    """Voice Assistant Service implementation (0x185E)."""

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.VOICE_ASSISTANT_NAME: True,
        CharacteristicName.VOICE_ASSISTANT_UUID: True,
        CharacteristicName.VOICE_ASSISTANT_SERVICE_CONTROL_POINT: True,
        CharacteristicName.INSTALLED_LOCATION: True,
        CharacteristicName.VOICE_ASSISTANT_SESSION_STATE: True,
        CharacteristicName.VOICE_ASSISTANT_SESSION_FLAG: True,
        CharacteristicName.VOICE_ASSISTANT_SUPPORTED_LANGUAGES: True,
        CharacteristicName.VOICE_ASSISTANT_SUPPORTED_FEATURES: True,
    }
