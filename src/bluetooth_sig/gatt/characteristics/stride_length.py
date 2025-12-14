"""Stride Length characteristic (0x2B49)."""

from __future__ import annotations

from ..constants import UINT16_MAX
from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class StrideLengthCharacteristic(BaseCharacteristic):
    """Stride Length characteristic (0x2B49).

    org.bluetooth.characteristic.stride_length

    Stride Length characteristic.
    """

    _template = ScaledUint16Template(scale_factor=0.001)  # 1mm resolution

    expected_length: int = 2
    min_value: float = 0.0
    max_value: float = UINT16_MAX * 0.001  # Max scaled value
    expected_type: type = float
