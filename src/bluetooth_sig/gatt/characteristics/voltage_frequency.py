"""Voltage Frequency characteristic implementation."""

from __future__ import annotations

from ...types.units import ElectricalUnit
from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class VoltageFrequencyCharacteristic(BaseCharacteristic):
    """Voltage Frequency characteristic (0x2BE8).

    org.bluetooth.characteristic.voltage_frequency

    Voltage Frequency characteristic.

    Measures voltage frequency with 1/256 Hz resolution.
    """

    _template = ScaledUint16Template(scale_factor=1 / 256)

    _manual_unit: str = ElectricalUnit.HERTZ.value  # Override template's "units" default
    resolution: float = 1 / 256
