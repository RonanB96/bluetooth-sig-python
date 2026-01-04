"""Hip Circumference characteristic (0x2A8F)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class HipCircumferenceCharacteristic(BaseCharacteristic[float]):
    """Hip Circumference characteristic (0x2A8F).

    org.bluetooth.characteristic.hip_circumference

    Hip Circumference characteristic.
    """

    _template = ScaledUint16Template(scale_factor=0.01)  # 1cm resolution
