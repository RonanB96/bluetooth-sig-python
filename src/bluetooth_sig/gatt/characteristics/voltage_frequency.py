"""Voltage Frequency characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class VoltageFrequencyCharacteristic(BaseCharacteristic):
    """Voltage Frequency characteristic.

    Measures voltage frequency with 1/256 Hz resolution.
    """

    _template = ScaledUint16Template()

    _characteristic_name: str = "Voltage Frequency"
    _manual_unit: str = "Hz"  # Override template's "units" default
    resolution: float = 1 / 256
