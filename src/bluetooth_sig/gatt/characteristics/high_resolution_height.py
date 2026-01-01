"""High Resolution Height characteristic (0x2B47)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class HighResolutionHeightCharacteristic(BaseCharacteristic):
    """High Resolution Height characteristic (0x2B47).

    org.bluetooth.characteristic.high_resolution_height

    High Resolution Height characteristic.
    """

    _template = ScaledUint16Template(scale_factor=0.01)  # 1cm resolution
