"""Battery level characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import PercentageTemplate


class BatteryLevelCharacteristic(BaseCharacteristic):
    """Battery level characteristic."""

    _template = PercentageTemplate()
