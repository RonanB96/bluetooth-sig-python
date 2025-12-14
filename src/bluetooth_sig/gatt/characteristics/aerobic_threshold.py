"""Aerobic Threshold characteristic (0x2A7E)."""

from __future__ import annotations

from ..constants import UINT8_MAX
from .base import BaseCharacteristic
from .templates import Uint8Template


class AerobicThresholdCharacteristic(BaseCharacteristic):
    """Aerobic Threshold characteristic (0x2A7E).

    org.bluetooth.characteristic.aerobic_threshold

    Aerobic Threshold characteristic.
    """

    expected_length = 1
    min_value = 0
    max_value = UINT8_MAX
    expected_type = int

    _template = Uint8Template()
