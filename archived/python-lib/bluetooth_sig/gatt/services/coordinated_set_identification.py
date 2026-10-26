"""CoordinatedSetIdentification Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class CoordinatedSetIdentificationService(BaseGattService):
    """Coordinated Set Identification Service implementation (0x1846).

    Identifies devices belonging to a coordinated set (e.g., left
    and right earbuds) for LE Audio.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.SET_IDENTITY_RESOLVING_KEY: True,
        CharacteristicName.COORDINATED_SET_SIZE: False,
        CharacteristicName.SET_MEMBER_LOCK: False,
        CharacteristicName.SET_MEMBER_RANK: False,
        CharacteristicName.COORDINATED_SET_NAME: False,
    }
