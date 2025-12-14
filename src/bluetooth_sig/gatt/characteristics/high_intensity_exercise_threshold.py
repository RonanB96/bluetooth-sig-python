"""High Intensity Exercise Threshold characteristic (0x2B4D)."""

from __future__ import annotations

from ..constants import UINT8_MAX
from .base import BaseCharacteristic
from .templates import Uint8Template


class HighIntensityExerciseThresholdCharacteristic(BaseCharacteristic):
    """High Intensity Exercise Threshold characteristic (0x2B4D).

    org.bluetooth.characteristic.high_intensity_exercise_threshold

    High Intensity Exercise Threshold characteristic.
    """

    expected_length = 1
    min_value = 0
    max_value = UINT8_MAX
    expected_type = int

    _template = Uint8Template()
