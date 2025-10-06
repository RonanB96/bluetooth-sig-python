"""High Voltage characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint24Template


class HighVoltageCharacteristic(BaseCharacteristic):
    """High Voltage characteristic.

    Measures high voltage systems using uint24 (3 bytes) format.
    """

    _template = ScaledUint24Template(scale_factor=1.0)

    _manual_unit: str = "V"  # Override template's "units" default
    resolution: float = 1.0
