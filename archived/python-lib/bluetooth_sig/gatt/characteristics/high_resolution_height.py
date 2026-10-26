"""High Resolution Height characteristic (0x2B47)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class HighResolutionHeightCharacteristic(BaseCharacteristic[float]):
    """High Resolution Height characteristic (0x2B47).

    org.bluetooth.characteristic.high_resolution_height

    High Resolution Height characteristic.
    """

    _template = ScaledUint16Template(scale_factor=0.0001)  # 0.1mm resolution (M=1, d=-4, b=0)
