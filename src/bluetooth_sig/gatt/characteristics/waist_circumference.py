"""Waist Circumference characteristic (0x2A97)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class WaistCircumferenceCharacteristic(BaseCharacteristic[float]):
    """Waist Circumference characteristic (0x2A97).

    org.bluetooth.characteristic.waist_circumference

    Waist Circumference characteristic.
    """

    _template = ScaledUint16Template(scale_factor=0.01)  # 1cm resolution
