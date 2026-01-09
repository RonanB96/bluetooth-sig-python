"""Average Voltage characteristic implementation."""

from __future__ import annotations

from ...types.units import ElectricalUnit
from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class AverageVoltageCharacteristic(BaseCharacteristic[float]):
    """Average Voltage characteristic (0x2AE1).

    org.bluetooth.characteristic.average_voltage

    Average Voltage characteristic.

    Measures average voltage with 1/64 V resolution.
    """

    _template = ScaledUint16Template(scale_factor=1 / 64)

    _manual_unit: str = ElectricalUnit.VOLTS.value  # Override template's "units" default
    resolution: float = 1 / 64
