"""Ranging Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class RangingService(BaseGattService):
    """Ranging Service implementation (0x185B).

    Provides distance measurement and ranging data between BLE
    devices using channel sounding.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.RAS_FEATURES: True,
        CharacteristicName.RAS_CONTROL_POINT: True,
        CharacteristicName.ON_DEMAND_RANGING_DATA: True,
        CharacteristicName.REAL_TIME_RANGING_DATA: False,
        CharacteristicName.RANGING_DATA_READY: True,
        CharacteristicName.RANGING_DATA_OVERWRITTEN: True,
    }
