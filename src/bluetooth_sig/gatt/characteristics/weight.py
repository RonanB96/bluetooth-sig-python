"""Weight characteristic (0x2A98)."""

from __future__ import annotations

from ..constants import UINT16_MAX
from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class WeightCharacteristic(BaseCharacteristic):
    """Weight characteristic (0x2A98).

    org.bluetooth.characteristic.weight

    Weight characteristic.
    """

    _template = ScaledUint16Template(scale_factor=0.005)  # 5g resolution

    # Validation attributes
    expected_length: int = 2
    min_value: float = 0.0
    max_value: float = UINT16_MAX * 0.005  # Max scaled value
    expected_type: type = float
