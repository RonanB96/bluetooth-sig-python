"""Height characteristic (0x2A8E)."""

from __future__ import annotations

from ..constants import UINT16_MAX
from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class HeightCharacteristic(BaseCharacteristic):
    """Height characteristic (0x2A8E).

    org.bluetooth.characteristic.height

    Height characteristic.
    """

    # Validation attributes
    expected_length: int = 2  # uint16
    min_value: float = 0.0
    max_value: float = UINT16_MAX * 0.01  # Max scaled value
    expected_type: type = float

    _template = ScaledUint16Template(scale_factor=0.01)  # 1cm resolution
