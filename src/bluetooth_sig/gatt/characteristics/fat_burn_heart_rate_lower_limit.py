"""Fat Burn Heart Rate Lower Limit characteristic (0x2A88)."""

from __future__ import annotations

from ..constants import UINT8_MAX
from .base import BaseCharacteristic
from .templates import Uint8Template


class FatBurnHeartRateLowerLimitCharacteristic(BaseCharacteristic):
    """Fat Burn Heart Rate Lower Limit characteristic (0x2A88).

    org.bluetooth.characteristic.fat_burn_heart_rate_lower_limit

    Fat Burn Heart Rate Lower Limit characteristic.
    """

    expected_length = 1
    min_value = 0
    max_value = UINT8_MAX
    expected_type = int

    _template = Uint8Template()
