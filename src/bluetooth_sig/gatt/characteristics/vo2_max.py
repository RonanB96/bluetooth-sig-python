"""VO2 Max characteristic (0x2A96)."""

from __future__ import annotations

from ..constants import UINT8_MAX
from .base import BaseCharacteristic
from .templates import Uint8Template


class VO2MaxCharacteristic(BaseCharacteristic):
    """VO2 Max characteristic (0x2A96).

    org.bluetooth.characteristic.vo2_max

    VO2 Max characteristic.
    """

    expected_length = 1
    min_value = 0
    max_value = UINT8_MAX
    expected_type = int

    _template = Uint8Template()  # ml/kg/min
