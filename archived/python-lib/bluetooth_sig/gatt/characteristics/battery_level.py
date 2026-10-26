"""Battery level characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import PercentageTemplate


class BatteryLevelCharacteristic(BaseCharacteristic[int]):
    """Battery Level characteristic (0x2A19).

    org.bluetooth.characteristic.battery_level

    Battery level characteristic.
    """

    _template = PercentageTemplate()
