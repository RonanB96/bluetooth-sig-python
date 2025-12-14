"""Heart Rate Max characteristic (0x2A8D)."""

from __future__ import annotations

from ..constants import UINT8_MAX
from .base import BaseCharacteristic
from .templates import Uint8Template


class HeartRateMaxCharacteristic(BaseCharacteristic):
    """Heart Rate Max characteristic (0x2A8D).

    org.bluetooth.characteristic.heart_rate_max

    Heart Rate Max characteristic.
    """

    # Validation attributes
    expected_length: int = 1  # uint8
    min_value: int = 0
    max_value: int = UINT8_MAX
    expected_type: type = int

    _template = Uint8Template()
