"""Anaerobic Threshold characteristic (0x2A83)."""

from __future__ import annotations

from ..constants import UINT8_MAX
from .base import BaseCharacteristic
from .templates import Uint8Template


class AnaerobicThresholdCharacteristic(BaseCharacteristic):
    """Anaerobic Threshold characteristic (0x2A83).

    org.bluetooth.characteristic.anaerobic_threshold

    Anaerobic Threshold characteristic.
    """

    expected_length = 1
    min_value = 0
    max_value = UINT8_MAX
    expected_type = int

    _template = Uint8Template()
