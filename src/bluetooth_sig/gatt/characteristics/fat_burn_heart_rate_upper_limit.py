"""Fat Burn Heart Rate Upper Limit characteristic (0x2A89)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class FatBurnHeartRateUpperLimitCharacteristic(BaseCharacteristic[int]):
    """Fat Burn Heart Rate Upper Limit characteristic (0x2A89).

    org.bluetooth.characteristic.fat_burn_heart_rate_upper_limit

    Fat Burn Heart Rate Upper Limit characteristic.
    """

    _template = Uint8Template()
