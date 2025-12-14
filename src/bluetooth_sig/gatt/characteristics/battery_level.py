"""Battery level characteristic implementation."""

from __future__ import annotations

from ..constants import PERCENTAGE_MAX
from .base import BaseCharacteristic
from .templates import PercentageTemplate


class BatteryLevelCharacteristic(BaseCharacteristic):
    """Battery Level characteristic (0x2A19).

    org.bluetooth.characteristic.battery_level

    Battery level characteristic.
    """

    # Validation attributes
    expected_length: int = 1  # uint8
    min_value: int = 0
    max_value: int = PERCENTAGE_MAX  # Percentage 0-100
    expected_type: type = int

    _template = PercentageTemplate()
