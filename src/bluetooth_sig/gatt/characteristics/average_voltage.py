"""Average Voltage characteristic implementation."""

from __future__ import annotations

from ...types.units import ElectricalUnit
from ..constants import UINT16_MAX
from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class AverageVoltageCharacteristic(BaseCharacteristic):
    """Average Voltage characteristic (0x2AE1).

    org.bluetooth.characteristic.average_voltage

    Average Voltage characteristic.

    Measures average voltage with 1/64 V resolution.
    """

    # Validation attributes
    expected_length: int = 2  # uint16
    min_value: float = 0.0
    max_value: float = UINT16_MAX * (1.0 / 64.0)  # Max scaled value
    expected_type: type = float

    _template = ScaledUint16Template(scale_factor=1 / 64)

    _manual_unit: str = ElectricalUnit.VOLTS.value  # Override template's "units" default
    resolution: float = 1 / 64
