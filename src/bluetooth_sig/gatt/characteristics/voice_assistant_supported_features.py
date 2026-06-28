"""Voice Assistant Supported Features characteristic (0x2C38)."""

from __future__ import annotations

from enum import IntFlag

from ..constants import SIZE_UINT8
from .base import BaseCharacteristic
from .templates import FlagTemplate


class VoiceAssistantSupportedFeatures(IntFlag):
    """Voice Assistant supported features bitfield."""

    SESSION_FLAGS_ENABLED = 1 << 0


class VoiceAssistantSupportedFeaturesCharacteristic(BaseCharacteristic[VoiceAssistantSupportedFeatures]):
    """Voice Assistant Supported Features characteristic (0x2C38).

    org.bluetooth.characteristic.voice_assistant_supported_features
    """

    expected_length = SIZE_UINT8
    _template = FlagTemplate.uint8(VoiceAssistantSupportedFeatures)
