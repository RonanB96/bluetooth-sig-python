"""Maximum Recommended Heart Rate characteristic (0x2A91)."""

from __future__ import annotations

from ..constants import UINT8_MAX
from .base import BaseCharacteristic
from .templates import Uint8Template


class MaximumRecommendedHeartRateCharacteristic(BaseCharacteristic):
    """Maximum Recommended Heart Rate characteristic (0x2A91).

    org.bluetooth.characteristic.maximum_recommended_heart_rate

    Maximum Recommended Heart Rate characteristic.
    """

    expected_length = 1
    min_value = 0
    max_value = UINT8_MAX
    expected_type = int

    _template = Uint8Template()
