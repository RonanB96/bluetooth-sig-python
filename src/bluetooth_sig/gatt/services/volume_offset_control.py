"""VolumeOffsetControl Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class VolumeOffsetControlService(BaseGattService):
    """Volume Offset Control Service implementation (0x1845).

    Provides per-output volume offset control for LE Audio devices.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.VOLUME_OFFSET_STATE: True,
        CharacteristicName.AUDIO_LOCATION: True,
        CharacteristicName.VOLUME_OFFSET_CONTROL_POINT: True,
        CharacteristicName.AUDIO_OUTPUT_DESCRIPTION: True,
    }
