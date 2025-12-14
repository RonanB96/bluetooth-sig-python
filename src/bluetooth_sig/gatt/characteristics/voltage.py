"""Voltage characteristic implementation."""

from __future__ import annotations

from ...types.units import ElectricalUnit
from ..constants import UINT16_MAX
from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class VoltageCharacteristic(BaseCharacteristic):
    """Voltage characteristic (0x2B18).

    org.bluetooth.characteristic.voltage

    Voltage characteristic.

    Measures voltage with 1/64 V resolution.
    """

    _template = ScaledUint16Template(scale_factor=1 / 64, offset=0)

    _manual_unit: str = ElectricalUnit.VOLTS.value  # Override template's "units" default

    # Template configuration
    resolution: float = 1 / 64  # 1/64 V resolution

    expected_length: int = 2
    min_value: float = 0.0
    max_value: float = UINT16_MAX * (1.0 / 64.0)  # Max scaled value
    expected_type: type = float
