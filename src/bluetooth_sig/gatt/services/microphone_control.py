"""MicrophoneControl Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class MicrophoneControlService(BaseGattService):
    """Microphone Control Service implementation (0x184D).

    Controls microphone mute state for LE Audio devices.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.MUTE: True,
    }
