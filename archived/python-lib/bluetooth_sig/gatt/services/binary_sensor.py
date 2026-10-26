"""BinarySensor Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class BinarySensorService(BaseGattService):
    """Binary Sensor Service implementation (0x183B).

    Enables devices with one or more binary (open/closed, on/off)
    sensors to report sensor state to a client device. Commands are
    received on the BSS Control Point and responses/events are
    indicated on the BSS Response characteristic.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.BSS_CONTROL_POINT: True,
        CharacteristicName.BSS_RESPONSE: True,
    }
