"""Battery Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class BatteryService(BaseGattService):
    """Battery Service implementation.

    Contains characteristics related to battery information:
    - Battery Level - Required
    - Battery Level Status - Optional
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.BATTERY_LEVEL: True,
        CharacteristicName.BATTERY_LEVEL_STATUS: False,
        CharacteristicName.ESTIMATED_SERVICE_DATE: False,
        CharacteristicName.BATTERY_CRITICAL_STATUS: False,
        CharacteristicName.BATTERY_ENERGY_STATUS: False,
        CharacteristicName.BATTERY_TIME_STATUS: False,
        CharacteristicName.BATTERY_HEALTH_STATUS: False,
        CharacteristicName.BATTERY_HEALTH_INFORMATION: False,
        CharacteristicName.BATTERY_INFORMATION: False,
        CharacteristicName.MANUFACTURER_NAME_STRING: False,
        CharacteristicName.MODEL_NUMBER_STRING: False,
        CharacteristicName.SERIAL_NUMBER_STRING: False,
    }
