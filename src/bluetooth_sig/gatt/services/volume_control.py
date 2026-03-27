"""VolumeControl Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class VolumeControlService(BaseGattService):
    """Volume Control Service implementation (0x1844).

    Controls audio volume and mute state for LE Audio devices.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.VOLUME_STATE: True,
        CharacteristicName.VOLUME_CONTROL_POINT: False,
        CharacteristicName.VOLUME_FLAGS: False,
    }
