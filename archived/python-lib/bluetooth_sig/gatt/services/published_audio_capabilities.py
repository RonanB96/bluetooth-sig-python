"""PublishedAudioCapabilities Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class PublishedAudioCapabilitiesService(BaseGattService):
    """Published Audio Capabilities Service implementation (0x1850).

    Publishes the audio capabilities of an LE Audio device including
    supported codec configurations and audio locations.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.AVAILABLE_AUDIO_CONTEXTS: True,
        CharacteristicName.SUPPORTED_AUDIO_CONTEXTS: True,
        CharacteristicName.SINK_PAC: False,
        CharacteristicName.SOURCE_PAC: False,
        CharacteristicName.SINK_AUDIO_LOCATIONS: False,
        CharacteristicName.SOURCE_AUDIO_LOCATIONS: False,
    }
