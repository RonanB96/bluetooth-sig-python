"""HearingAccess Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class HearingAccessService(BaseGattService):
    """Hearing Access Service implementation (0x1854).

    Provides hearing aid functionality for LE Audio devices including
    preset management and feature reporting.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.HEARING_AID_FEATURES: True,
        CharacteristicName.HEARING_AID_PRESET_CONTROL_POINT: False,
        CharacteristicName.ACTIVE_PRESET_INDEX: False,
    }
