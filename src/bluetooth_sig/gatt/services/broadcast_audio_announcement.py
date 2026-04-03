"""BroadcastAudioAnnouncement Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class BroadcastAudioAnnouncementService(BaseGattService):
    """Broadcast Audio Announcement Service implementation (0x1852).

    Used in LE Audio broadcast advertisements to announce
    broadcast audio stream availability.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {}
