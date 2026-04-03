"""BasicAudioAnnouncement Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class BasicAudioAnnouncementService(BaseGattService):
    """Basic Audio Announcement Service implementation (0x1851).

    Used in LE Audio broadcast source advertisements to announce
    basic audio stream parameters.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {}
