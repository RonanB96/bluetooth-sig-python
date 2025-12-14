"""Two Zone Heart Rate Limits characteristic (0x2A95)."""

from __future__ import annotations

from ..constants import UINT8_MAX
from .base import BaseCharacteristic
from .templates import Uint8Template


class TwoZoneHeartRateLimitsCharacteristic(BaseCharacteristic):
    """Two Zone Heart Rate Limits characteristic (0x2A95).

    org.bluetooth.characteristic.two_zone_heart_rate_limits

    Two Zone Heart Rate Limits characteristic.
    """

    expected_length = 1
    min_value = 0
    max_value = UINT8_MAX
    expected_type = int

    _template = Uint8Template()
