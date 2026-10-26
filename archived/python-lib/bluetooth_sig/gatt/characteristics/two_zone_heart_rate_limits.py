"""Two Zone Heart Rate Limits characteristic (0x2A95)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class TwoZoneHeartRateLimitsCharacteristic(BaseCharacteristic[int]):
    """Two Zone Heart Rate Limits characteristic (0x2A95).

    org.bluetooth.characteristic.two_zone_heart_rate_limits

    Two Zone Heart Rate Limits characteristic.
    """

    _template = Uint8Template()
