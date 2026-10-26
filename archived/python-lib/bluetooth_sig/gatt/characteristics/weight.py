"""Weight characteristic (0x2A98)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class WeightCharacteristic(BaseCharacteristic[float]):
    """Weight characteristic (0x2A98).

    org.bluetooth.characteristic.weight

    Weight characteristic.
    """

    _template = ScaledUint16Template(scale_factor=0.005)  # 5g resolution

    # Validation attributes
