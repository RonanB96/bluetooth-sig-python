"""Average Voltage characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class AverageVoltageCharacteristic(BaseCharacteristic):
    """Average Voltage characteristic.

    Measures average voltage with 1/64 V resolution.
    """

    _template = ScaledUint16Template(scale_factor=1 / 64)

    _manual_unit: str = "V"  # Override template's "units" default
    resolution: float = 1 / 64
