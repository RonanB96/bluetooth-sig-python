"""TelephonyAndMediaAudio Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class TelephonyAndMediaAudioService(BaseGattService):
    """Telephony and Media Audio Service implementation (0x1855).

    Combines telephony and media audio profiles for LE Audio devices
    (TMAP).
    """

    _service_name: str = "Telephony and Media Audio"

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.TMAP_ROLE: True,
    }
