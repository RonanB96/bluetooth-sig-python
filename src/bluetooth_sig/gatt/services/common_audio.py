"""CommonAudio Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class CommonAudioService(BaseGattService):
    """Common Audio Service implementation (0x1853).

    Provides common audio profile functionality shared across
    LE Audio use cases.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {}
