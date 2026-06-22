"""Generic Voice Assistant Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class GenericVoiceAssistantService(BaseGattService):
    """Generic Voice Assistant Service implementation (0x185F)."""

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.VOICE_ASSISTANT_SUPPORTED_LANGUAGES: True,
        CharacteristicName.VOICE_ASSISTANT_SUPPORTED_FEATURES: True,
    }
