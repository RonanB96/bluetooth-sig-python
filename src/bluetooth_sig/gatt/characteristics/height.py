"""Height characteristic (0x2A8E)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class HeightCharacteristic(BaseCharacteristic[float]):
    """Height characteristic (0x2A8E).

    org.bluetooth.characteristic.height

    Height characteristic.
    """

    _template = ScaledUint16Template(scale_factor=0.01)  # 1cm resolution
