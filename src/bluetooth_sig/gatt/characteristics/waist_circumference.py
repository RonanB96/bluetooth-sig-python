"""Waist Circumference characteristic (0x2A97)."""

from __future__ import annotations

from ..constants import UINT16_MAX
from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class WaistCircumferenceCharacteristic(BaseCharacteristic):
    """Waist Circumference characteristic (0x2A97).

    org.bluetooth.characteristic.waist_circumference

    Waist Circumference characteristic.
    """

    _template = ScaledUint16Template(scale_factor=0.01)  # 1cm resolution

    expected_length: int = 2
    min_value: float = 0.0
    max_value: float = UINT16_MAX * 0.01  # Max scaled value
    expected_type: type = float
