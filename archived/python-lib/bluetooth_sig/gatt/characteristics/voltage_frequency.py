"""Voltage Frequency characteristic implementation."""

from __future__ import annotations

from ...types.units import ElectricalUnit
from .base import BaseCharacteristic
from .templates import Uint16Template


class VoltageFrequencyCharacteristic(BaseCharacteristic[int]):
    """Voltage Frequency characteristic (0x2BE8).

    org.bluetooth.characteristic.voltage_frequency

    Voltage Frequency characteristic.

    Measures voltage frequency with resolution of 1 Hz (M=1, d=0, b=0).
    """

    _template = Uint16Template()

    _manual_unit: str = ElectricalUnit.HERTZ.value  # Override template's "units" default
    resolution: float = 1.0
    max_value: int = 65533  # Exclude special values 0xFFFE and 0xFFFF
