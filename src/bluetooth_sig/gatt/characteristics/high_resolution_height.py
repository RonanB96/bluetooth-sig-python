"""High Resolution Height characteristic (0x2B47)."""

from __future__ import annotations

from ..constants import UINT16_MAX
from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class HighResolutionHeightCharacteristic(BaseCharacteristic):
    """High Resolution Height characteristic (0x2B47).

    org.bluetooth.characteristic.high_resolution_height

    High Resolution Height characteristic.
    """

    expected_length = 2
    min_value = 0.0
    max_value = UINT16_MAX * 0.01  # Max scaled value
    expected_type = float

    _template = ScaledUint16Template(scale_factor=0.01)  # 1cm resolution
