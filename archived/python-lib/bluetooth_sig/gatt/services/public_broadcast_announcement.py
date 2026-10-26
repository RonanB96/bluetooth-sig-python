"""PublicBroadcastAnnouncement Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class PublicBroadcastAnnouncementService(BaseGattService):
    """Public Broadcast Announcement Service implementation (0x1856).

    Used for public LE Audio broadcast announcements that can be
    received without prior pairing.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {}
