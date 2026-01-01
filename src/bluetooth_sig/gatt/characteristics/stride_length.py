"""Stride Length characteristic (0x2B49)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class StrideLengthCharacteristic(BaseCharacteristic):
    """Stride Length characteristic (0x2B49).

    org.bluetooth.characteristic.stride_length

    Stride Length characteristic.
    """

    _template = ScaledUint16Template(scale_factor=0.001)  # 1mm resolution
