"""High Intensity Exercise Threshold characteristic (0x2B4D)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class HighIntensityExerciseThresholdCharacteristic(BaseCharacteristic):
    """High Intensity Exercise Threshold characteristic (0x2B4D).

    org.bluetooth.characteristic.high_intensity_exercise_threshold

    High Intensity Exercise Threshold characteristic.
    """

    _template = Uint8Template()
