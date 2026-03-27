"""BroadcastAudioScan Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class BroadcastAudioScanService(BaseGattService):
    """Broadcast Audio Scan Service implementation (0x184F).

    Enables scanning for and synchronising with LE Audio broadcast
    sources.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.BROADCAST_AUDIO_SCAN_CONTROL_POINT: False,
    }
