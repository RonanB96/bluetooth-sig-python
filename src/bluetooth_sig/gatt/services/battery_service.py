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
        CharacteristicName.BATTERY_LEVEL: True,  # required
        CharacteristicName.BATTERY_LEVEL_STATUS: False,  # optional
    }
