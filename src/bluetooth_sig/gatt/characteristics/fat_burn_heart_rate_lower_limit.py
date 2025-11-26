"""Fat Burn Heart Rate Lower Limit characteristic (0x2A88)."""

from .base import BaseCharacteristic
from .templates import Uint8Template


class FatBurnHeartRateLowerLimitCharacteristic(BaseCharacteristic):
    """Fat Burn Heart Rate Lower Limit characteristic (0x2A88).

    org.bluetooth.characteristic.fat_burn_heart_rate_lower_limit

    Fat Burn Heart Rate Lower Limit characteristic.
    """

    _template = Uint8Template()
