"""Maximum Recommended Heart Rate characteristic (0x2A91)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class MaximumRecommendedHeartRateCharacteristic(BaseCharacteristic[int]):
    """Maximum Recommended Heart Rate characteristic (0x2A91).

    org.bluetooth.characteristic.maximum_recommended_heart_rate

    Maximum Recommended Heart Rate characteristic.
    """

    _template = Uint8Template()
