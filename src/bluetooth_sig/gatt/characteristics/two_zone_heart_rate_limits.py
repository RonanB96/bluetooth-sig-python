"""Two Zone Heart Rate Limits characteristic (0x2A95)."""

from .base import BaseCharacteristic
from .templates import Uint8Template


class TwoZoneHeartRateLimitsCharacteristic(BaseCharacteristic):
    """Two Zone Heart Rate Limits characteristic (0x2A95).

    org.bluetooth.characteristic.two_zone_heart_rate_limits

    Two Zone Heart Rate Limits characteristic.
    """

    _template = Uint8Template()
