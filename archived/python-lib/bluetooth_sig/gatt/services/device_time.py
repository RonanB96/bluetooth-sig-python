"""DeviceTime Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class DeviceTimeService(BaseGattService):
    """Device Time Service implementation (0x1847).

    Provides device time management including time synchronisation,
    feature reporting, and time adjustment control.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.DEVICE_TIME_FEATURE: True,
        CharacteristicName.DEVICE_TIME_PARAMETERS: True,
        CharacteristicName.DEVICE_TIME: True,
        CharacteristicName.DEVICE_TIME_CONTROL_POINT: True,
        CharacteristicName.TIME_CHANGE_LOG_DATA: False,
        CharacteristicName.RECORD_ACCESS_CONTROL_POINT: False,
    }
