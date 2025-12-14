"""Fat Burn Heart Rate Upper Limit characteristic (0x2A89)."""

from __future__ import annotations

from ..constants import UINT8_MAX
from .base import BaseCharacteristic
from .templates import Uint8Template


class FatBurnHeartRateUpperLimitCharacteristic(BaseCharacteristic):
    """Fat Burn Heart Rate Upper Limit characteristic (0x2A89).

    org.bluetooth.characteristic.fat_burn_heart_rate_upper_limit

    Fat Burn Heart Rate Upper Limit characteristic.
    """

    expected_length = 1
    min_value = 0
    max_value = UINT8_MAX
    expected_type = int

    _template = Uint8Template()
