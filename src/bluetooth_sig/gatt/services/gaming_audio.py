"""GamingAudio Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class GamingAudioService(BaseGattService):
    """Gaming Audio Service implementation (0x1858).

    Provides gaming-optimised audio profiles for LE Audio devices
    with low-latency audio streaming capabilities.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.GMAP_ROLE: True,
        CharacteristicName.UGG_FEATURES: False,
        CharacteristicName.UGT_FEATURES: False,
        CharacteristicName.BGR_FEATURES: False,
        CharacteristicName.BGS_FEATURES: False,
    }
